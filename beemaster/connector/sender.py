
class Sender(object):


	def __init__(self, address, port):
		self.address = address
		self.port = port


	def send(self, data):
		print("Sender should send '{}'' to {}:{}".format(data, self.address, self.port))
		return True