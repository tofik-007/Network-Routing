from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

class LinearTopo(Topo):
    def build(self, n=6):
        # Create switches
        switches = [self.addSwitch(f's{i}') for i in range(1, n + 1)]

        # Create hosts and link them to respective switches
        for i, switch in enumerate(switches):
            host = self.addHost(f'h{i+1}', ip=f'10.0.0.{i+1}/8')
            self.addLink(host, switch)

        # Connect switches in a linear topology
        for i in range(len(switches) - 1):
            self.addLink(switches[i], switches[i + 1])

if __name__ == '__main__':
    setLogLevel('info')
    topo = LinearTopo()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)
    net.start()
    print("Linear topology is running.")
    net.pingAll()
    CLI(net)
    net.stop()
