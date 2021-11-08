class servers:
	serverCount = 0
	def __init__(self, name, state, port, rcon):
		if(port <= 1025 or port >= 65535):
			port = 25565 #FIXME configport
		if(rcon <= 1025 or rcon >= 65535):
			rcon = 25545 #FIXME configrcon
			
		self.name = name
		self.state = state
		self.port = port
		self.rcon = rcon

		servers.serverCount += 1

	#name set/get
	@property
	def name(self):
		return self.__name
	@name.setter #FIXME name should be read-only
	def name(self, name):
		self.__name = name
	
	#state set/get
	@property
	def state(self):
		return self.__state
	@state.setter
	def state(self, state):
		self.__state = state
	
	#port set/get
	@property
	def port(self):
		return self.__port
	@port.setter
	def port(self, port):
		self.__port = port

	#rcon set/get
	@property
	def rcon(self):
		return self.__rcon
	@rcon.setter
	def rcon(self, rcon):
		self.__rcon = rcon

	# port checking
	def isAlive(self):
		pass
		#isAlive?

	# Other
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


print(server[0].name)
server[0].name = 'S2'
server[0].state = 2
server[0].port = 24444
server[0].rcon = 44442
print(server[0].name)


for x in range(len(server)):
	print(f'IsOnline: {server[x].isOnline()}')
	server[x].printData()
	print(server[x].getData())

print(f'Ci sono: {servers.count} server')


#online = {onlineId: ['Server', state, port, rcon]}