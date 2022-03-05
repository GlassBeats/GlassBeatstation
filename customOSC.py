from pythonosc import udp_client, dispatcher, osc_server

class OSC_Sender():
    def __init__(self, ipaddr="127.0.0.1", port=9951):
        self.osc_client = udp_client.SimpleUDPClient(ipaddr, port)

    def send(self, addr, arg):
        self.osc_client.send_message(addr, arg)

