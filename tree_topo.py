from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class TreeTopo(Topo):
    def build(self, depth=2, fanout=2):
        def add_tree_level(parent, depth, fanout):
            if depth == 0:
                return

            for i in range(fanout):
                # Create switches for this level
                switch = self.addSwitch(f's{depth}-{i}')
                self.addLink(parent, switch)

                # Add hosts at leaf level
                if depth == 1:
                    host = self.addHost(f'h{depth}-{i}', ip=f'10.0.{depth}.{i}/24')
                    self.addLink(switch, host)
                else:
                    add_tree_level(switch, depth - 1, fanout)

        # Create root switch and start recursion
        root_switch = self.addSwitch('s0')
        add_tree_level(root_switch, depth, fanout)

if __name__ == '__main__':
    setLogLevel('info')

    # Create topology
    topo = TreeTopo(depth=3, fanout=2)  # Adjust depth and fanout as needed
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6653),
        link=TCLink
    )

    # Start network
    net.start()
    print("Tree topology is running.")

    # Test connectivity
    net.pingAll()

    # Launch CLI
    CLI(net)

    net.stop()
