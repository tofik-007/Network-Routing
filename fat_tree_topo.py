from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

class FatTreeTopo(Topo):
    def build(self, k=4):
        core_switches = []
        for i in range(k // 2):
            core_switch = self.addSwitch(f'core{i + 1}')
            core_switches.append(core_switch)

        for pod in range(k):
            agg_switches = []
            for i in range(k // 2):
                agg_switch = self.addSwitch(f'agg{pod}-{i + 1}')
                self.addLink(core_switches[i], agg_switch)
                agg_switches.append(agg_switch)

            for i in range(k // 2):
                edge_switch = self.addSwitch(f'edge{pod}-{i + 1}')
                self.addLink(agg_switches[i], edge_switch)

                for j in range(2):
                    host = self.addHost(f'h{pod}-{i}-{j}', ip=f'10.{pod}.{i}.{j}/8')
                    self.addLink(edge_switch, host)

if __name__ == '__main__':
    setLogLevel('info')
    topo = FatTreeTopo(k=4)  # Customize `k` as needed
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)

    net.start()
    print("Fat-tree topology is running.")
    net.pingAll()
    CLI(net)
    net.stop()
