from receiver import Receiver
from mapper import Mapper
from sender import Sender


class Connector(object):
    def __init__(self, ):
        super(Connector, self).__init__()
        
        self.mapper = Mapper({'some': 'mapping'})
        self.sender = Sender('127.0.0.1', 5000)
        self.receiver = Receiver("bm-connector", '0.0.0.0', 8080)
        self.receiver.listen("/", self.handle_receive)

    def handle_receive(self, message):
        # TODO: implement me
        print("Connector received:", message)
        mapped = self.mapper.map(message)
        print("Mapped message is", mapped)
        success = self.sender.send(mapped)
        print("Connector did its job? ", success)

        
if __name__ == '__main__':
    connector = Connector()