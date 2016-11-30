
class Mapper(object):


	def __init__(self, mapping):
		self.mapping = mapping


	def map(self, toMap):
		print("Mapper should map", toMap)
		return "xxx-some-broker-msg-xxx"