from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, ipv4, arp
from ryu.lib.packet import ether_types
from ryu.lib import hub
from ryu.topology import event
from ryu.topology.api import get_all_link, get_all_switch
from ryu.app.gui_topology.gui_topology import GUITopology  # Importing GUI topology

class QoSController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # Declare that this app depends on GUITopology
    _CONTEXTS = {'gui_topology': GUITopology}

    def __init__(self, *args, **kwargs):
        super(QoSController, self).__init__(*args, **kwargs)
        self.gui_topology = kwargs['gui_topology']  # Assign the GUI topology context
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.links = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.datapaths[datapath.id] = datapath
        self.install_default_flows(datapath)

    def install_default_flows(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Default flow: match all traffic and send to NORMAL processing
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        # Process flow statistics to identify congestion
        for stat in ev.msg.body:
            self.logger.info("Flow Stats: %s", stat)

    def _monitor(self):
        # Periodically request stats to monitor flows
        while True:
            for dp in self.datapaths.values():
                self.request_stats(dp)
            hub.sleep(10)

    def request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(event.EventLinkAdd)
    def link_add_handler(self, ev):
        # Handle new link detection
        link = ev.link
        self.links[(link.src.dpid, link.dst.dpid)] = link
        self.logger.info("New Link Added: %s", link)

    @set_ev_cls(event.EventLinkDelete)
    def link_delete_handler(self, ev):
        # Handle link removal
        link = ev.link
        self.links.pop((link.src.dpid, link.dst.dpid), None)
        self.logger.info("Link Removed: %s", link)
