from receiver import Receiver


class Connector(object):
    def __init__(self, ):
        super(Connector, self).__init__()
        self.start_receiver()

    def start_receiver(self):
        receiver = Receiver("bm-connector", '0.0.0.0', 8080)
        receiver.listen("/", self.handle_receive)

    def handle_receive(self, message):
        print("Connector received: %s", message)

        
if __name__ == '__main__':
    connector = Connector()