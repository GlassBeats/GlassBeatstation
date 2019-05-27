from pythonosc import udp_client

osc_client = udp_client.SimpleUDPClient("localhost", 9951)

class playloops():
    def __init__(self):
        osc_client.send("/loop_add", [2, 40.0])
        osc_client.send("/sl/{}/register_auto_update".format(""), ["state", 10, "localhost:9998", "/sloop"])
