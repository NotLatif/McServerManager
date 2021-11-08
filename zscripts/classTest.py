class servers:
	def __init__(self, name, state, port, rcon):
		self.name = name
		self.state = state
		self.port = port
		self.rcon = rcon

	def setState(self, state):
		self.state = state
	
	def setPort(self, port):
		self.port = port
	
	def setRcon(self, rcon):
		self.rcon = rcon

	def isOnline(self):
		if self.state == 1:
			return True
		else:
			return False

	def printData(self):
		print(f'Server {self.name}, State {self.state}, Port {self.port}, Rcon {self.rcon}')

	def getData(self):
		return([self.name, self.state, self.port, self.rcon])


server = []
server.append(servers("S0", 0, 2665, 352))
server.append(servers("S1", 1, 2666, 353))
server.append(servers("S2", 0, 2667, 354))
server.append(servers("S3", 1, 2668, 355))
server.append(servers("S4", 2, 2669, 356))

server[0].setRcon(2442)
server[0].setState(2)
for x in range(len(server)):
	print(f'IsOnline: {server[x].isOnline()}')
	server[x].printData()
	print(server[x].getData())


#online = {onlineId: ['Server', state, port, rcon]}