# TODO FIXME, CHANGED, XXX, IDEA, HACK, NOTE, REVIEW, NB, BUG, QUESTION, COMBAK, TEMP, DEBUG, OPTIMIZE
from colorama.ansi import Back


try:
	import os
	import subprocess
	import time
	import keyboard
	import random
	import traceback
	import shutil
	import configobj
	import socket
	import json
	from colorama import Fore, Style, init
	from distutils.dir_util import copy_tree
	from configobj import ConfigObj
	from datetime import datetime
	from shutil import copyfile
	from zipfile import ZipFile
	from mcrcon import MCRcon
	from requests import get
	from glob import glob
	init()
except ModuleNotFoundError:
	print('FATAL \n' + str(traceback.format_exc()))
	input('Premere invio per interrompere')

print(Style.BRIGHT)

log = True
maxBackupFolders = 15
maxServers = 0
rconPort = 25575
rconPsw = 'Rcon69Psw'
batPlaceholderText = 'cd *PATH*\njava *MaxHeap* -jar *JARFILE* nogui' #FIXME 10: should be loaded at script startup

run = True
now = str(datetime.now().strftime('%d-%m-%Y_%H_%M_%S'))
logNow = str(datetime.now().strftime('%Y-%m-%d_%H_%M_%S'))
logFile = str(f'logs\\{logNow}.txt') 

extIp = get('https://api.ipify.org').text

#back = {}
#back{id: [aaId, date, [IDs]}

server = [] #Will contain Servers objects
class Servers:
	serverCount = 0
	def __init__(self, name, state, port, rcon):
		mPrint('DEV', f'Called class contructor Servers({name}, {state}, {port}, {rcon})')
		if(port <= 1025 or port >= 65535):
			port = int(config['server-port'])
		if(rcon <= 1025 or rcon >= 65535):
			rcon = int(config['rcon-port'])
			
		self.name = name	#char: folder name
		self.state = state	#0: offline | 1: online | 2: restarting
		self.port = port	#server-port
		self.rcon = rcon	#rcon-port
		#self.psw = psw		#rcon-password
		Servers.serverCount += 1

	#name set/get
	@property
	def name(self):
		return self.__name
	@name.setter #FIXME name should be read-only
	def name(self, name):
		self.__name = name
	
	@property
	def state(self):
		return self.__state
	@state.setter
	def state(self, state):
		try:
			state = int(state)
			if not (0 <= state <= 2): ##OMG THIS IS SO COOL WTFFF
				state = None
		except ValueError:
			state = state.lower()
			if state == 'online':
				state = 1
			elif state == 'offline':
				state = 0
			elif state == 'restarting':
				state = 2
			else:
				state = None

		if(state == None):
			mPrint('FATAL', 'Incorrect server state')
			crash()
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

	# Object functions
		## return online state
	def isOnline(self):
		mPrint('FUNC', f'Servers.isOnline(self)')
		if self.state == 1:
			return True
		else:
			return False

	def setParam(self, param, value):
		mPrint('FUNC', f'Servers.setParam(self, {param}, {value})')
		if(param == 'name'):
			self.name = value
		elif(param == 'state'):
			self.state = value
		elif(param == 'port'):
			self.port = value
		elif(param == 'rcon'):
			self.rcon = value
		else:
			mPrint('ERROR', f'Wrong value for Servers.setParam({param}, {value})')

	def getData(self):
		mPrint('FUNC', f'Servers.getData(self)')
		return([self.name, self.state, self.port, self.rcon])
	
	# Class Functions
		## port checking
	def isAlive(ip, port):
		mPrint('FUNC', f'Servers.isAlive({ip}, {port})')
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			alive = s.connect_ex((ip, port)) == 0
			return alive
	
	def isAliveUpdate(self, ip, port):
		mPrint('FUNC', f'Servers.isAliveUpdate({ip}, {port})')
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			alive = s.connect_ex((ip, port)) == 0
			if self.isOnline() and (not alive):
				mPrint('WARN', f'Il server risultava online, ma è in realtà offline. Aggiorno il dato')
				self.state = 0
			elif (not self.isOnline()) and (alive):
				mPrint('WARN', f'Il server risultava offline, ma è in realtà online. Aggiorno il dato')
				self.state = 1
			return alive

backup = []
class Backups:
	def __init__(self, aaID,  date, serverIDs: list):
		self.aaID = aaID
		self.date = date
		self.serverIDs = serverIDs
		print(f'Backups({aaID}, {date}, {serverIDs})')

	@property
	def aaID(self):
		return self.__aaID
	@aaID.setter
	def aaID(self, newID):
		self.__aaID = newID
	
	@property
	def date(self):
		return self.__date
	@aaID.setter
	def date(self, newDate):
		self.__date = newDate

	@property
	def serverIDs(self):
		return self.__serverIDs
	@serverIDs.setter
	def serverIDs(self, newIDs):
		self.__serverIDs = newIDs

	def getMin(self):
		return self.date[-2:]
	
	def getTimeDate(self):
		return self.date[:-3]
	
	def backAAtoId(backupID):
		try:
			int(backupID)
		except ValueError:
			backupAA = backupID
			for x in range(len(server)):
				if backup[x].aaID == backupAA:
					backupID = x
		else:
			backupID = int(backupID)
		return backupID

class Cfg(): # too much work to do rn, will COMBAK later
	pass

class makeTellraw:
	##Code is not mine, but can't find the source
    text = ''
    color = 'white'
    bold = False

    def __init__(self, **kwargs):
        self.__json = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k, v)
        self.__format_mc()

    def __format_mc(self):
        self.__to_add('text', self.text)
        self.__to_add('bold', self.bold)
        if checkColor(self.color):
            self.__to_add('color', self.color)

    def __to_add(self, key, value):
        if value is not False and value is not None:
            self.__json[key] = value

    def get_json(self):
        return json.dumps(self.__json, separators=(',', ':'))

    @staticmethod
    def multiple_tellraw(*tellraws):
        return_list = ','.join(str(tellraw) for tellraw in tellraws)
        # Double quote is add to avoid parent heriarchy of Events
        return '["",' + return_list + ']'

    def __str__(self):
        return self.get_json()
def checkColor(color):
    if color == 'dark_red':
        return True
    elif color == 'red':
        return True
    elif color == 'gold':
        return True
    elif color == 'yellow':
        return True
    elif color == 'dark_green':
        return True
    elif color == 'green':
        return True
    elif color == 'aqua':
        return True
    elif color == 'blue':
        return True
    elif color == 'dark_blue':
        return True
    elif color == 'light_purple':
        return True
    elif color == 'white':
        return True
    elif color == 'gray':
        return True
    elif color == 'dark_gray':
        return True
    elif color == 'black':
        return True
    else:
        return False

#  ----------- Script Functions -----------
def prtStackTrace(Fatal = False): #prints most recent error
	'''
		Simple test
	'''
	if Fatal:
		mPrint('FATAL', '\n' + traceback.format_exc())
		global run
		run = False
	else:
		mPrint('ERROR', '\n' + traceback.format_exc())

def createLog(): #creates logFile
	if not os.path.exists('logs'): #crea la dir log se non esiste
		os.mkdir('logs')
	if not os.path.isfile(logFile): #crea il file logs\{now} se non esiste
		data = 'Welcome to the log lmao nothing useful here? Probabli not.\n'
		data = data + 'I present to you the complete mess of this script\n\n'
		writeDataFile(logFile, data) #first commit
	else:
		mPrint('FUNC', f'createLog()') #log file exists??? wtf how (impossible)
		mPrint('DEV', f'File già presente: {logFile}') #actually too scared to delete this who knows

def logToFile(newdata): #logs data to logFile
	File = getDataFile(logFile)
	File = File + str(newdata) + '\n'
	writeDataFile(logFile, File)

def yesNoInput(input): #parses (Y/n) format input
	input = input.lower()
	if (input == 'y' or input == '' or input == 'yes'):
		mPrint('INFO', 'Comand accettato')
		return 'y'
	else:
		mPrint('INFO', 'Comand annullato')
		return 'n'

def rPrint(text, reqlog=False): #Prints data without colors/prefixes
	mPrint(text, '', reqlog, True)

def mPrint(prefix, text='', reqlog=False, raw=False): #Formats data with date/prefixes/colors for better readibility
	now = datetime.now().strftime('%d-%m-%Y, %H:%M:%S')
	res = Fore.RESET
	col = Fore.RESET

	if prefix == 'INFO':
		col = Fore.GREEN
	elif prefix == 'WARN':
		col = Fore.YELLOW
	elif prefix == 'ERROR' or prefix == 'FATAL':
		col = Fore.RED
	elif prefix == 'DEV' or prefix == 'WORK':
		col = Fore.MAGENTA
		reqlog = True
	elif prefix == 'FUNC':
		col = Fore.BLACK
		reqlog = True
	elif prefix == 'RESP':
		col = Fore.CYAN
	elif prefix == 'IMPORTANT':
		col = Fore.RED
	else:
		text = prefix

	if raw:
		if reqlog == True:
			if log == True:
				logToFile(text)
				print(text)
				return 1
			else:
				if devLogs:
					logToFile(text)
					return 1
		else:
			logToFile(text)
			print(text)
			return 1
	else:
		if reqlog == True:
			if log == True:
				out = f'[{now}]: {col}[{prefix}] - {text}{res}'

			else:
				if devLogs:
					logToFile(f'[{now}]: [{prefix}] - {text}')
				return 2
		else:
			out = f'[{now}]: {col}[{prefix}] - {text}{res}'

		logToFile(f'[{now}]: [{prefix}] - {text}')
		print(out)
		return 0

#properties.ini
def checkConfig(): #Checks if properties.ini has the required entries
	mPrint('FUNC', f'checkConfig()')
	r=0
	file = ConfigObj('properties.ini')
	if 'server-ip' not in file:
		file['server-ip'] = "192.168.1.x"
		r = 1
	if 'server-port' not in file:
		file['server-port'] = 25565
	if '-Xmx' not in file:
		file['-Xmx'] = '4G'
	if 'max-backup-folders' not in file:
		file['max-backup-folders'] = 15
	if 'log' not in file:
		file['log'] = False
	if 'developer-logs' not in file:
		file['developer-logs'] = True
	if 'autobackup-delay-minutes' not in file:
		file['autobackup-delay-minutes'] = 20

	file.write()
	remQuote('properties.ini')
	return r

def createConfig(): #Creates properties.ini HAS TO BE UPDATED MANUALLY
	mPrint('FUNC', f'createConfig()')
	config = configobj.ConfigObj()
	config.filename = 'properties.ini'
	config['server-ip'] = "192.168.1.x"
	config['server-port'] = 25565
	config['-Xmx'] = '4G'
	config['log'] = False
	config['developer-logs'] = True
	config['max-backup-folders'] = 15
	config['autobackup-delay-minutes'] = 20
	config.write()
	remQuote('properties.ini')

def updateConfig(key, value): #Stores an updated config in the properties.ini file
	mPrint('FUNC', f'updateConfig({key}, {value})')
	config[key] = value
	config.write()
	remQuote('properties.ini')
	
def getProperty(key, serverID): #pull and return info from server.properties files
	mPrint('FUNC', f'getProperty({key}, {serverID})')
	key = str(key)
	path = serverID + '\\server.properties'
	temp_cfg = ConfigObj(path)
	if key in temp_cfg:
		return int(temp_cfg[key])
	else:
		return -1


def crash(): #lol does it work if it crashes the program? (yes because it just stops it)
	mPrint('FUNC', f'crash()')
	exit()

def remQuote(file):#removes '"' from files for compatibility issues
	data = getDataFile(file) #apre e prende i dati
	data = data.replace('"','') #toglie gli "
	writeDataFile(file, data) #apre e riscrive i dati
def getDataFile(file): #apre file e prende i dati
	file = open(file, "rt")
	data = file.read()
	file.close()
	return data
def writeDataFile(file, data): #apre file e scrive dati
	file = open(file, "wt")
	file.write(data)
	file.close()

def verifyStatus(serverID): #checks if server has succesfully started pinging the port
	mPrint('FUNC', f'verifyStatus({serverID})')
	if serverID < 0:
		pass
	else:
		if serverID <= Servers.serverCount:
			startTime = time.time()
			beginTime = time.time()
			seconds = 7
			mPrint('INFO', 'Controllo lo stato del server tra 7 secondi...')
			mPrint('INFO', 'Non dare nessun comando fino a quando ho finito.')
			mPrint('INFO', f'{Fore.CYAN} \'Q\' per annullare{Fore.RESET}')
			while True:
				currentTime = time.time()
				elapsedTime = currentTime - startTime
				if elapsedTime > seconds:
					mPrint('INFO', 'controllo...')
					if Servers.isAlive(config['server-ip'], server[serverID].port):
						mPrint('INFO', f'Server: {server[serverID].name} è stato rilevato. ({round(currentTime-beginTime)}sec.)')
						server[serverID].state = 'online'
						break
					else:
						mPrint('INFO', 'Offline.')
						mPrint('INFO', 'Riprovo tra 10 secondi...')
					startTime = time.time()
				try:
					if keyboard.is_pressed('q'):
						server[serverID].state = 'online'
						mPrint('WARN', f'Questo server ora risulterà online.')
						mPrint('INFO', f'Usa il comando \'stop {serverID}\' se vuoi farlo risultare offline.')
						break
				except:
					pass
		else:
			mPrint('ERROR', 'Server non trovato.')

def loadServers(): #scans the directory and adds the servers in the server[] List as objects -> server[Servers s1, Servers s2, ...] 
	mPrint('FUNC', f'loadServers()')
	s = dirGrab()
	x = 0
	for serverName in s:
		#proprietà dei server.properties
		sPort = getProperty('server-port', serverName)
		rPort = getProperty('rcon.port', serverName)
		if sPort < 0:
			mPrint('ERROR', f'valore server-port non valido nel server: {serverName}')
			mPrint('INFO', 'porto la server-port a 25565.') ##SOLO UN PLACEHOLDER, VERRÀ CAMBIATO DURANTE IL LOADING
			sPort = int(config['server-port'])
		if sPort >= int(config['rcon-port']):
			mPrint('WARN', f'server: {serverName} ha una porta >= a { config["rcon-port"] }.')
			mPrint('INFO', 'per evitare problemi porto la server-port a 25565.')
			sPort = 25565
		server.append(Servers(str(serverName), 0, sPort, rPort)) #Create Servers objects
		x += 1
	mPrint('INFO', f'Loaded {x} servers.')

	mPrint('INFO', 'Imposto automaticamente le porte rcon dei server.')
	changeProperties('all', -1, False)
	rconSync()
	batFixer(-1, config['-Xmx'])
	backSync()

def batter(i, batCopy, serverID, s): #adds start.bat to server folder configured for script usage
	mPrint('FUNC', f'batter({i}, {batCopy}, {serverID}, {s})')
	
	path = server[i].name + '\\start.bat' # possible BUG: what if server folders don't match with server count?
	if not os.path.isfile(path):
		mPrint('IMPORTANT', f'IL FILE {path} NON ESISTE. Ne creo uno nuovo')
		mPrint('IMPORTANT', f'controlla che il server si chiami {server[i].name}\\server.jar')
		try:
			data = getDataFile('zscripts\\placeholder.bat')
			writeDataFile(path, data)
		except FileNotFoundError:
			writeDataFile('zscripts\\placeholder.bat', batPlaceholderText)
			writeDataFile(path, data)

	mPrint('WORK', f'start.bat path: {path}')
			
	jarFile = getDataFile(server[i].name+'\\start.bat')
	File = jarFile.split(' ')

	mPrint('DEV', File) 
	for x in range(len(File)): #BUG server.jar must be called 'server.jar' for this to work
		if '.jar' in File[x]:
			jarFile = File[x]
			break
		else:
			jarFile = 'server.jar'
			
	batCopy = batCopy.replace('*JARFILE*', jarFile)
	batCopy = batCopy.replace('*PATH*', server[i].name)
	writeDataFile(path, batCopy)
	mPrint('DEV', 'batcopy: '+batCopy)

def batFixer(serverID, xmx = None): #creates a raw batch file and sends it to batter ^ 
	mPrint('FUNC', f'batFixer({serverID}, {xmx})')
	#gets raw data and make raw bat file (and sends it to batter())
	if xmx == None:
		xmx = config['-Xmx']

	s = Servers.serverCount # TEST

	placeholder = 'zscripts\\placeholder.bat'
	try:
		batCopy = getDataFile(placeholder)
	except FileNotFoundError:
		writeDataFile(placeholder, batPlaceholderText)
		batCopy = getDataFile(placeholder)

	try:
		if 'G' in str(xmx):
			num = xmx.replace('G', '')
			xmx = str(int(int(num)*1024))
		elif 'M' in str(xmx):
			num = xmx.replace('M', '')
			xmx = num
		else:
			mPrint('WARN', 'Invalid -Xmx format, check properties.ini')
			mPrint('WARN', 'Temporarily setting -Xmx to -Xmx2048M')
			xmx = '2048'
	except:
		prtStackTrace()
		return -1

	batCopy = batCopy.replace('*MaxHeap*', f'-Xmx{xmx}M')

	if serverID == -1:
		for x in range(s):
			batter(x, batCopy, serverID, s)	
	else:
		x = serverID
		batter(x, batCopy, serverID, s)

def changeSingleProperty(key, value, serverID):# changes only one property for a specific (server.properties) file
	""" chenges one propery for a specific serverID
	key -> server.properties key
	value -> key value
	serverID -> int
	server/server.properties -> key=value
	"""
	mPrint('FUNC', f'startChangeProperties({key}, {value}, {serverID})')

	serverDir = server[serverID].name + '\\server.properties'
	
	temp_cfg = ConfigObj(serverDir)
	temp_cfg[key] = value
	temp_cfg.write()
	remQuote(serverDir)

def rconSync(rconPort = -1): #sets an rconPort for all the servers found
	rconPort = int(config['rcon-port']) if (rconPort == -1) else int(rconPort)
	mPrint('FUNC', f'rconSync({rconPort})')
	if rconPort < int(config['rcon-port']):
		mPrint('WARN', f'rcon.port è impostato a {rconPort}')
		mPrint('WARN', f'per prevenire problemi con le porte usate dai server')
		mPrint('WARN', f'Impostare un numero maggiore/uguale a 25575.')
		mPrint('WARN', f'Tenere in considerazione le porte utilizzate per tenere i server online.')
		return -1

	for x in range(Servers.serverCount):
		if server[x].isOnline():
			mPrint('ERROR', 'Ho rilevato un server online,')
			mPrint('WARN', 'per evitare problemi chiudi tutti i server con il comando \'stop\'')
			mPrint('WARN', 'se credi sia un errore aggiorna la lista server online usando il comando \'ls -f\'')
			mPrint('WARN', 'anche il comando \'set help\' potrebbe aiutarti')
			return -2

	mPrint('INFO', 'rcon.port sync')
	mPrint('DEV', f'rconSync(rconPort={rconPort})')
	s = dirGrab()


	x = 0
	for serverDir in s:
		path = serverDir + '\\server.properties'
		if os.path.isfile(path):
			mPrint('INFO', f'Found path {path}')
			temp_cfg = ConfigObj(path)

			newRcon = rconPort+x
			if 'enable-rcon' in temp_cfg:
				mPrint('INFO', 'changing rcon.port to: ' + str(newRcon))
				temp_cfg['rcon.port'] = newRcon
				temp_cfg['rcon.password'] = rconPsw
				temp_cfg['enable-rcon'] = 'true'
				temp_cfg.write()
				remQuote(path)
			else:
				mPrint('INFO', 'creating rcon settings to: ' + str(newRcon))
				temp_cfg['enable-rcon'] = 'true'
				if not 'rcon.port' in temp_cfg:
					temp_cfg['rcon.password'] = newRcon
				if not 'rcon.password' in temp_cfg:
					temp_cfg['rcon.password'] = rconPsw
				temp_cfg.write()
				remQuote(path)
			x+=1

def workChangeProperties(key, serverName): #syncs specific property in (server.properties || start.bat) whith the config stored in (properties.ini)
	mPrint('FUNC', f'workChangeProperties({key}, {serverName})')
	serverName = serverName + '\\server.properties'
	temp_cfg = ConfigObj(serverName)
	
	mPrint('DEV', f'serverName:{serverName}')

	#parsing
	if key == 'ip':
		key ='server-ip'
	elif key == 'port':
		key ='server-port'
	elif key == 'ram' or key == 'xmx':
		key = '-Xmx'

	else: #trusting changeProperties() parsing
		key = key

	if key == '-Xmx':
		for x in range(Servers.serverCount):
			batFixer(x, config['-Xmx'])
		return 0
	if key == 'all':
		temp_cfg['server-ip'] = config['server-ip']
		temp_cfg['server-port'] = config['server-port']
		mPrint('INFO', 'changed ip and port to: ' + config['server-ip'] + ":" + str(config['server-port']) + ' for server: '+str(serverName))
	else:
		temp_cfg[str(key)] = config[str(key)]
		mPrint('INFO', 'server: '+ str(serverName))
		mPrint('INFO', 'changed key: ' + key + ", to value:" + temp_cfg[key])
	temp_cfg.write()

	#chiama remQuote per togliere i '"'
	remQuote(serverName)
			
def changeProperties(key, serverID=-1, syncRcon=True): #prepares data for workChangeProperties()
	mPrint('FUNC', f'changeProperties({key}, {serverID})')
	mPrint('INFO', 'key: ' + str(key))

	dirs = dirGrab()
	#initial parse
	if (key != 'ip' and key != 'server-ip' and key != 'port' and key != 'server-port' and key != 'all' and key != 'ram' and key != 'xmx' and key != '-Xmx'):
		mPrint('ERROR', 'key error.')
		return 69

	if serverID < 0: #cambia tutti i server
		mPrint('DEV', 'All servers')
		for name in dirs:
			workChangeProperties(key, name)
	else: #cambia il server scelto
		mPrint('DEV', f'Server {serverID}')
		workChangeProperties(key, dirs[int(serverID)])

	if syncRcon:
		rconSync()

	return 0

#Config modifiers (properties.ini AND server.properties)
def modIp(newIp, sync=True): #changes ip config to newIp (user input)
	mPrint('FUNC', f'modIp({newIp}, {sync})')
	if not (newIp == '' or newIp.count('.')!=3):
		updateConfig('server-ip', newIp)

		mPrint('DEV', 'config[\'server-ip\'] = '+str(config['server-ip']))
		mPrint('DEV', 'ip = ' + str(config['server-ip']))
	else:
		mPrint('WARN', 'Wrong ip format x.x.x.x')

	if sync:
		mPrint('INFO', 'Sincronizzo gli ip a tutti i server')
		changeProperties('server-ip')

def modPort(newPort, sync=True): #changes port config to newPort (user input)
	mPrint('FUNC', f'modPort({newPort}, {sync})')
	if not (newPort == '' and newPort.isnumeric() == False and int(newPort) >= 0):
		if newPort >= int(config['rcon-port']):
			mPrint('ERROR', 'server-port can\'t be >= than 25575 for rcon to work.')
			return -1
		else:
			updateConfig('server-port', newPort)

		mPrint('DEV', 'config[\'server-port\'] = '+str(config['server-port']))
		mPrint('DEV', 'port = ' + str(config['server-port']))
	else:
		mPrint('WARN', 'Wrong port format')

	if sync:
		mPrint('INFO', 'Sincronizzo le porte a tutti i server')
		changeProperties('server-port')

def modRam(xmx, serverID=-1): #changes ram to (user input) in properties.ini
	if not str(serverID).replace('-', '').isnumeric():
		serverID = txtToId(serverID)

	serverID = int(serverID)
	
	if not('G' in str(xmx) or 'M' in str(xmx)):
		mPrint('ERROR', 'Invalid -Xmx format, \'xmx help\'')
		return -1

	if serverID == -1:
		updateConfig('-Xmx', xmx)

		for x in range(Servers.serverCount):
			batFixer(x, xmx)
	elif serverID < Servers.serverCount:
		batFixer(serverID, xmx)
	else:
		mPrint('ERROR', 'Server non trovato!')

############################################################################

def dirGrab(isStart = True): #Returns a list containing server folders in alphabetical order ##works but can be updated
	mPrint('FUNC', f'dirGrab({isStart})')
	#Ottengo una lista raw delle cartelle in questa directory
	r_dirs = glob(os.path.join('.', "*", ""))
	#La rielaboro in qualcosa di utilizzabile
	for x in r_dirs:
		dirs = [x[2:-1] for x in r_dirs]
	#Cerco il file "server.properties" or "config.yml" in ogni directory.
	#Se il file è presente, esiste un server (in teoria)
	if(isStart == True):
		mPrint('WORK', 'Scanning for server.properties')
		#Controllo se c'è un server.properties
		for x in range(len(dirs)):
			if dirs[x] == 'backups':
				dirs[x] = '[F*3bd45]'
				continue

			if(os.path.isfile(dirs[x]+r'\server.properties') == False) and (os.path.isfile(dirs[x]+r'\config.yml') == False):
				mPrint('WORK', 'Found missing server.properties:')
				rPrint('\t| dir: '+dirs[x], True)
				rPrint('\t| x  : '+str(x), True)
				dirs[x] = '[F*3bd45]'
				
		i = 0
		while True: #elimino dalla lista le cartelle che non hanno il server.properties
			if(i+1 > len(dirs)):
				break
			mPrint('WORK', 'Checking x (F*3bd45) at index: ' + str(i))
			mPrint('WORK', 'dirs[x]: ' + str(dirs[i]))
			if(dirs[i] == '[F*3bd45]'):
				dirs.pop(i)
				mPrint('WORK', 'popped at x: ' + str(i))
			else:
				i = i+1
			
	mPrint('DEV', 'dirGrab()->dirs: ')
	mPrint('DEV', dirs)
	#Ritorno una lista di directory elaborate
	return dirs

def ls(): #lists the server that the script has found
	mPrint('FUNC', f'ls()')
	dirs = dirGrab()
	count = 0
	rPrint('------Server Trovati------')
	rPrint('Green = Online')
	for x in range(len(dirs)):
		if server[x].state == 1:
			pre = Fore.GREEN
			aft = server[x].port
		else:
			pre = Fore.RESET
			aft = ''
		rPrint(f'{pre}{x}|-> {server[x].name} {aft}{Fore.RESET}')
		count += 1
	print('\n')

def listOnline(check=False): # returns a list of online servers (for printOnline() to print)
	mPrint('FUNC', f'listOnline({check})')

	onList = []

	for x in range(Servers.serverCount):
		if server[x].state != 0:
			onList.append(x)
			mPrint('INFO', f'Found online server: {server[x].name}')
			mPrint('DEV', f'Server info, id: {x}, state: {server[x].state}, port: {server[x].port}, rcon: {server[x].rcon}')
	if check:
		for x in range(Servers.serverCount):
			if server[x].state != 0:
				if Servers.isAlive(config['server-ip'], server[x].port):
					server[x].state = 1
					mPrint('DEV', f'found True Online Server {server[x].name} with id: {x}, is now in state {server[x].state}')
				else:
					server[x].state = 0
					onList.remove(x)
					mPrint('DEV', f'found False Online Server {server[x].name} with id: {x}, is now in state {server[x].state}')
	return onList

def printOnline(check=False): # prints a list of online servers
	mPrint('FUNC', f'printOnline({check})')
	onlineServers = listOnline(check)
	rPrint('------Server Online------')
	rPrint(f'{config["server-ip"]} | {extIp}')
	if len(onlineServers) == 0:
		rPrint(' |-> No online server found.')
		rPrint(' |-> GOOD')
	else:
		for x in onlineServers:
			rPrint(str(x) + '|-> ' + server[x].name + ', ' + str(server[x].port))
	print('\n')

def sendRcon(serverID, command, text = None): # sends message to server using minecraft rcon protocol
	mPrint('FUNC', f'sendRcon({serverID}, {command}, {text})')

	if text is None:
		if '/' in command:
			send = f'{command}'
		else:
			send = f'/{command}'
	else:
		if '/' in command:
			send = f'{command} {text}'
		else:
			send = f'/{command} {text}'
		
	mPrint('DEV', 'Invio un comando al server: ' + send)
	mPrint('DEV', f'attempting rcon communication, \n\tserver: {serverID}\n\tcommand: {command}\n\ttext: {text}\n\tsend: {send}')
	mPrint('DEV', f'connection informations: \n\tip: {config["server-ip"]}\n\tpsw: {rconPsw}\n\tport: {server[serverID].rcon}')

	try:
		with MCRcon(config['server-ip'], rconPsw, server[serverID].rcon) as mcr:
			resp = mcr.command(send)
			mPrint('RESP', 'server resp: ' + resp)
	except ConnectionRefusedError:
		mPrint('INFO', 'I think some error occured? I\'ll just log it lol')
		mPrint('DEV', traceback.format_exc())
	except Exception:
		prtStackTrace()

def start(serverID, port=None):#Starts one/all server/s
	mPrint('FUNC', f'start({serverID}, {port})')
	serverID = str(serverID)

	#Preparation
	try: #If serverID is literal ('Server1') change to id, else cast int jtbs
		serverID = int(serverID)
	except ValueError:
		mPrint('WORK', 'Server is literal, scanning for xd')
		serverID = txtToId(serverID)
		
	if serverID != -1:
		mPrint('WORK', 'found serverID: ' + str(serverID))
	else:
		mPrint('ERROR', 'Server non trovato :(')
		return -1

	if port is None:
		port = int(config['server-port'])
	else:
		mPrint('INFO', 'running on custom server port: ' + str(port))
		port = int(port)
		changeSingleProperty('server-port', port, serverID)

	s = dirGrab()
	#Start
	if serverID >= Servers.serverCount:
		mPrint('WARN', f'Il server {serverID} non esiste, ho rilevato solo {Servers.serverCount} server')
		mPrint('INFO', 'Il comando \'ls -u\' aggiorna la lista server!')
		return -1

	for x in range(Servers.serverCount):
		if s[serverID] == server[x].name and server[x].state != 0: #Controllo se il server che sto facendo partire si già online
			mPrint('INFO', 'Controllo lo stato del server...')
			if Servers.isAlive(config['server-ip'], port):
				mPrint('WARN', 'Server già partito, annullo il comando')
				mPrint('WARN', 'La porta ' + config['server-ip'] +':'+str(port) + ' è attualmente occupata. Impossibile startare un server')
				return -1
			else:
				mPrint('INFO', f'Server segnalato online in realtà è offline, aggiorno lo stato per il server {serverID}')
				server[x].state = 0

		if port == server[x].port and server[x].state != 0: #FIXME 1 egualianze inutili e potrebbero rompere il codice, controlla invece se la porta è occupata a prescindere
			mPrint('INFO', 'Controllo lo stato del server...')
			if Servers.isAlive(config['server-ip'], port):
				mPrint('WARN', f'Esiste un server online su questa porta: {port}')
				mPrint('INFO', 'Provo con le prossime 5 porte...')
				starterP = port
				for y in range(1, 5):
					port = port+y
					if Servers.isAlive(config['server-ip'], port):
						mPrint('INFO', f'{port} non disponibile.')
					else:
						mPrint('WARN', f'Porta {port} libera, uso questa.')
						port = port
						changeSingleProperty('server-port', port, x)
						break
				if port == starterP+5:
					mPrint('ERROR', f'Nessun server trovato su 6 porte a partire da {starterP}')
					return 0

	mPrint('WORK', f'building server path for server id <{str(serverID)}>')
	file = s[serverID]+r'\start.bat'
	mPrint('WORK', f'builded path for {str(s[serverID])} ({file})')

	try:
		p = subprocess.Popen(file, creationflags=subprocess.CREATE_NEW_CONSOLE)
		mPrint('INFO', 'Server initialized.')
		server[serverID].state = 1 #[name,STATE,port,rcon]
		server[serverID].port = port

		mPrint('INFO', 'Verifico lo stato del server...')
		verifyStatus(serverID)
		mPrint('INFO', 'Condividi il tuo ip per far entrare anche gli altri!')
		if port != '25565':
			mPrint('INFO', f'{extIp}:{port}')
		else:
			mPrint('INFO', f'{extIp}')

	except Exception:
		mPrint('ERROR', 'C\'è stato un problema: printing Traceback:')
		prtStackTrace()

def stop(serverID = None, Force = False): #Stops one/all server/s
	mPrint('FUNC', f'stop({serverID})')

	#preparazione
	if serverID is not None:
		try:
			if serverID.isnumeric() == False:
				mPrint('WORK', 'Server is not numeric')
				serverID = txtToId(serverID)
				mPrint('WORK', f'server = {serverID}')
			else:
				serverID = int(serverID)
		except AttributeError:
			mPrint('WORK', 'Server is numeric')
			serverID = int(serverID)

	if serverID is None: #no input -> online/check if multiple are on
		mPrint('WORK', 'Server is None')
		count = 0
		for x in range(Servers.serverCount): #check server state, if online check reachability
			if server[x].state == 1:
				if Servers.isAlive(config['server-ip'], server[x].port): #is server online?
					if Servers.isAlive(config['server-ip'], server[x].rcon): #is rcon listening?
						mPrint('FATAL', f'La porta rcon per il server {x} non è in ascolto, sarà impossibile chiudere questo server.')
						count += 1
						serverID = x
				else:
					mPrint('WORK', f'server {x} was fake online')
					server[x].state = 0

		if count == 0: #no server found online
			mPrint('INFO', 'Nessun server trovato online!, \'ls help\'')
			return -1
		elif count == 1: #one server found online
			serverID = serverID
		else: #multiple servers found online
			mPrint('INFO', 'Piú di un server trovato online.')
			serverID = -1
		mPrint('WORK', f'server = {server}')

	if serverID == -1:
		mPrint('WORK', 'Checking all servers')
		for x in range(Servers.serverCount):
			if(server[x].state):
				try:
					splash = getSplash('stop')
					sendRcon(x,'tellraw @a', str(makeTellraw(text=splash, color='green', bold=True)))
				except Exception:
					prtStackTrace()
	else: # only one server is online
		mPrint('WORK', 'Checking one server')
		try:
			splash = getSplash('stop')
			sendRcon(serverID,'tellraw @a', str(makeTellraw(text=splash, color='green', bold=True)))
		except Exception:
			prtStackTrace()

	mes = str(makeTellraw(text='Server is going bye bye, confirm in python script pls', color='red', bold=True))
	#those send
	if serverID < 0: #-1| target all online server
		for x in range(Servers.serverCount):
			if server[x].state == 1:
				try:
					sendRcon(x, 'tellraw @a', mes)
				except Exception:
					prtStackTrace()
		if not Force:
			mPrint('WARN', 'Do you want to stop all the servers?')
			command = yesNoInput(input('(Y/n) > '))
			logToFile('> ' + command)
		else:
			command = 'y'

		if command != 'y':
			mPrint('INFO', 'Comando stop annullato')
			mPrint('INFO', f'I server rimarranno online.')
			return -2
		#else
		for x in range(Servers.serverCount):
			if server[x].state == 1:
				try:
					mPrint('INFO', 'mando una richiesta al server...')
					sendRcon(x, 'stop')
					server[x].state = 0
				except Exception:
					prtStackTrace()
			else:
				mPrint('INFO', f'Il server {server[x].name} è già offline')
				mPrint('INFO', f'Aggiorno le impostazioni...')
				server[x].state = 0
				mPrint('INFO', 'Fatto!')
				mPrint('DEV', f'server[x].state is now: {server[x].state}')
	else: # only target one server
		if serverID >= Servers.serverCount:
			mPrint('WARN', f'Il server {serverID} non esiste, ho rilevato solo {Servers.serverCount} server')
			mPrint('INFO', 'Il comando \'ls -u\' aggiorna la lista server!')
		else:
			if server[serverID].state == 1:
				sendRcon(serverID, 'tellraw @a', mes)
				if not Force:
					mPrint('WARN', 'Do you want to stop the server?')
					command = yesNoInput(input('(Y/n) > '))
					logToFile('> ' + command)
				else:
					command = 'y'

				if command == 'y':
					try:
						mPrint('INFO', 'mando una richiesta al server...')
						sendRcon(serverID, 'stop')
						server[serverID].state = 0
					except Exception:
						prtStackTrace()
				else:
					mPrint('INFO', 'Comando stop annullato')
					mPrint('INFO', f'Il server {server[serverID].name} è ancora online.')
					return -2

			else:
				mPrint('INFO', f'Il server {server[serverID].name} è già offline')
				mPrint('INFO', f'Aggiorno le impostazioni...')
				server[serverID].state = 0
				mPrint('INFO', 'Fatto!')
				mPrint('DEV', f'server[server].state is now: {server[serverID].state}')
				return -1

def restart(serverID = None): #Restarts on/all server/s
	mPrint('FUNC', f'restart({serverID})')

	if serverID == None:
		mPrint('INFO', 'Provo a riavviare tutti i server.')
		stopping = []
		for x in range(Servers.serverCount):
			if server[x].state == 1:
				stopping.append(x)
		if len(stopping) == 0:
			mPrint('INFO', 'Non ho trovato nessun server online!')
			mPrint('INFO', 'usa: \'check help\' per aiuto')
			mPrint('DEV', '\'set help\' per aiuto')
			return 0

		rPrint(f'Vuoi davvero riavviare {len(stopping)} server?')
		command = yesNoInput(input('(Y/n)> '))
		if command != 'y':
			logToFile(f'> {command}')
			return 0

		logToFile(f'> {command}')
		for x in range(len(stopping)):
			stop(x, True)
			server[x].state = 2
		for x in range(len(stopping)):
			start(x)

	else:
		if str(serverID).isnumeric():
			serverID = int(serverID)
		else:
			serverID = txtToId(serverID)
			if str(serverID).isnumeric():
				mPrint('ERROR', 'Server non trovato.')

		mPrint('INFO', f'Provo a riavviare il server {serverID}.')

		try:
			stop(serverID, True)
			server[serverID].state = 2
			time.sleep(5) ##FIXME 2 <<<<<<<<<< maybe get a return from rcon?? IDK MAYBE MULTITHREADING!!!!
			start(serverID)
		except Exception:
			prtStackTrace()

def txtToId(serverName): #Converts server name to server id
	mPrint('FUNC', f'txtToId({serverName})')
	serverID = 0 
	for serverFound in dirGrab():
		if serverFound == serverName:
			mPrint('WORK', f'returning: {serverID}')
			return serverID
		serverID += 1
	return -1

def set(serverID, param, value = None):
	mPrint('FUNC', f'set({serverID}, {param}, {value})')
	mPrint('WARN', 'Usare questa funzione solo se necessario.')

	if not str(serverID).isnumeric(): #if serverID is not numeric turn it into ID
		serverID = txtToId(serverID)
		if serverID == -1: #server ID not found
			print('ERROR', 'Nessun server trovato, prova con un id! \'ls\'')
			return -1
		
	if value != None: #raw from comand
		server[serverID].setParam(param, value)
		return 0

	try: #from program #PARAM SHOULD ONLY BE 0/1/2/online/offline/restarting, SINCE CMD IS FOR DEV USE THE CODE TRUSTS USER INPUT
		server[serverID].state = param
		mPrint('INFO', f'Il server {server[serverID].name} ora risulta {param}.')

	except Exception:
		prtStackTrace()

def check(param, port=0): #Add command 'check [port|id|-f]' default: 25565 checks if server is online and updates online{}
	mPrint('FUNC', f'check({param}, {port})')
	try:
		param = int(param)
	except Exception:
		param = txtToId(param)

	if Servers.serverCount > param >= 0: #if False then param is a port
		if param >= Servers.serverCount:
			mPrint('Server non trovato, \'ls -u\' per aggiornare la lista')
			return -1
		if port == 0:
			if Servers.isAlive(config['server-ip'], server[param].port):
				mPrint('INFO', 'Server is online.')
				server[param].state = 1
				return 1
			else:
				mPrint('INFO', 'Server is offline')
				server[param].state = 0
				return 0
		else:
			if Servers.isAlive(config['server-ip'], port):
				mPrint('INFO', 'Server is online.')
				server[param].state = 1
				server[param].port = port
				return 1
			else:
				mPrint('INFO', 'Server is offline')
				server[param].state = 0
				return 0
	else:
		if Servers.isAlive(config['server-ip'], param):
			mPrint('INFO', 'Un server è attivo su questa porta.')
			mPrint('INFO', 'Provvedo a sincronizzarlo per te, ma devi darmi l\'id del server!')
			ls()
			
			while True:
				s = input('[id]> ')
				if check(s) != -1:
					if not Servers.isAlive(config['server-ip'], server[s].rcon):
						mPrint('ERROR', 'La porta rcon non è disponibile, perfavore riavvia il server per evitare problemi.')
					else:
						break
		else:
			mPrint('INFO', f'Nessun server è attivo sulla porta {param}!')
			
def getSplash(menu = 'default'): #gets a fun text to send with rcon
	if menu == 'default':
		lst = 'zscripts\\spl\\splashes.txt'
	elif menu == 'stop':
		lst = 'zscripts\\spl\\stopSplashes.txt'
	elif menu == 'backup':
		lst = 'zscripts\\spl\\backSplashes.txt'
	lst = getDataFile(lst)
	d = lst.split('\n')
	return random.choice(d)

def abort(method): #implemented as a MEME, WARNING, -f WILL NOT SAVE DATA, -b IS NOT GUARANTEED TO SAVE YOUR DATA only use as a meme
	mPrint('FUNC', f'abort({method})')
	if method == '-f':
		mPrint('IMPORTANT', 'You have 5 seconds to save everything')
		time.sleep(5)
		os.system('shutdown /s /t 1')
	elif method == '-b':
		makeBackup(-1)
		os.system('shutdown /s /t 1')

def rconSave(serverID): #TODO check if this works
	sendRcon(serverID, 'save-all')

def backSync(): # Ricarica da capo i backup
	mPrint('FUNC', f'backSync()')
	if not os.path.exists('backups'):
		os.mkdir('backups')
		mPrint('INFO', 'Created backup directory.')
		
	folder = os.listdir(".\\backups")
	x = 0
	
	for x in range(len(backup)):
		backup.pop()

	for x in range(len(folder)):
		sub = os.listdir(f".\\backups\\{folder[x]}")
		if len(sub) == 0:
			shutil.rmtree(f'backups\\{folder[x]}')
			folder = os.listdir(".\\backups")
			mPrint('WORK', 'Cartella vuota.')
		else:
			backup.append(Backups(num_string(x+1), folder[x], sub))
			mPrint('WORK', f'[{num_string(x)}, {folder[x]}, {sub}]')
			x+=1

def backList(serverID = -1): # ???
	mPrint('FUNC', f'backList()')
	backSync()
	rPrint(f'{Fore.GREEN}|--------- BACKUPS ---------{Fore.RESET}')
	if serverID == -1:
		for x in range(len(backup)):
			rPrint(f'{Fore.MAGENTA}|->{backup[x].date}{Fore.RESET} (ID: {backup[x].aaID})')
			for j in range(len(backup[x].serverIDs)):
				rPrint(f'{Fore.MAGENTA}|{Fore.RESET}|({j})-> {backup[x].serverIDs[j]}')
			rPrint('|')
	else:
		for x in range(len(backup)):
			if server[serverID].name in backup[x].serverIDs:
				rPrint('|')
				rPrint(f'{Fore.MAGENTA}|->{backup[x].date}{Fore.RESET} (ID: {backup[x].date})')
				rPrint(f'{Fore.MAGENTA}|{Fore.RESET}|({x})-> {server[serverID].name}')
	rPrint(f'{Fore.GREEN}|--------------------------\n{Fore.RESET}')

def makeBackup(serverID=-2): #-1: all; -2:online
	mPrint('FUNC', f'makeBackup({serverID})')
	if(len(server) == 0):
		mPrint('ERROR', 'Non esiste nessun server!')
	if not os.path.exists('backups'):
		os.mkdir('backups')
		mPrint('INFO', 'Created backup directory.')

	if serverID==-1: #all
		for x in range(Servers.serverCount):
			makeBackup(x)
	elif serverID==-2: #online
		for x in range(Servers.serverCount):
			if server[x].state == 1 and server[x].isAliveUpdate():
				makeBackup(x)
	else: #specific serverID
		if not(0 <= serverID <= Servers.serverCount): #serverID is in range of existing servers
			mPrint('WARN', f'Server {server} non trovato.')
			return -2

		now = datetime.now().strftime('%Y-%m-%d_%H-%M') #folder name format

		if os.path.exists(f'backups\\{now}\\{server[serverID].name}'): #if backup already present
			mPrint('ERROR', f'Hai creato un backup per il server "{server[serverID].name}" meno di un minuto fa!')
		else: #can backup, save servers if online
			if server[serverID].state == 1 and server[serverID].isAliveUpdate():
				splash = getSplash('backup')
				sendRcon(serverID,'tellraw @a', str(makeTellraw(text=splash, color='yellow', bold=True)))
				rconSave(serverID)
			
			#checks if server backup already exists in one minute range
			if(os.path.exists(f'backups\\{now}\\{server[serverID].name}') is False):
				backDir = f'backups\\{now}\\{server[serverID].name}' #if path does not exist, we can make backup
			else:
				mPrint('Error', f'Hai creato un backup per {server[serverID].name} meno di un minuto fa.')
				return -3 # if path no exist, we no make backup
			
			try: #attempts to make dir for date if not already present
				os.mkdir(f'backups\\{now}')
			except FileExistsError:
				pass
				
			Folders = next(os.walk('backups'))[1] #what? REVIEW COMBAK later
			if len(Folders) > int(config['max-backup-folders']): #REVIEW TEST CODE
				n = len(Folders) - int(config['max-backup-folders'])
				for x in range(n):
					mPrint('WARN', 'Il numero di backup supera il limite, elimino le cartelle in più?')
					Folders = next(os.walk('backups'))[1]
					rem = min(Folders)
					path = f'backups\\{rem}'
					mPrint('WARN', f'Posso eliminare il backup {path} per fare spazio, continuo?')
					if(yesNoInput(input('(Y/n) > '))):
						shutil.rmtree(path)
					else:
						return -1

			os.mkdir(backDir)
			copy_tree(server[serverID].name, backDir)

			mPrint('INFO', f'Fatto ({server[serverID].name})')
			backSync()

def autobackup(): #FIXME 3
	backNames = []
	''' UNCOMMENT THIS LATER
	for x in range(Servers.serverCount):
		if server[i].state == 1:
			if Servers.isAlive(config['server-ip'], server[i].port):
				backNames.append(server[i].name)
	if len(backNames) <= 0:
		mPrint('WARN', 'Nessun server rilevato online, autobackup funziona solo per i server online.')
		return 0
	else:
		return backNames
	'''
	for x in range(Servers.serverCount):
		backNames.append(server[x].name)
	return backNames

def delbackup(backupID):
	mPrint('FUNC', f'delbackup({backupID})')
	backSync()

	backupID = Backups.backAAtoId(backupID)

	nServer = len(backup[backupID].serverIDs)
	mPrint('WARN', f'Sono presenti {nServer} server nel backup')
	mPrint('WARN', f'Sei sicuro di voler eliminare il backup del giorno {backup[backupID].date}?')
	mPrint('WARN', 'QUEI DATI ANDRANNO PERSI PER SEMPRE (un sacco di tempo)')
	
	if yesNoInput(input('(Y/n)> ')) == 'y':
		logToFile('(Y/n)> Y')
		path = 'backups\\' + backup[backupID].date
		try:
			shutil.rmtree(path)
		except FileNotFoundError:
			pass
	backSync()

def restorebackup(server): #COMBAK implement function
	mPrint('FUNC', f'restorebackup({server})')
	pass

def num_string(n): #Transforms number to char -> 1=a, 26=z, 27=aa, 53=ba...
	string = ""
	while n > 0:
		n, remainder = divmod(n - 1, 26)
		string = chr(65 + remainder) + string
	return string.lower()

def help(): #general command descriptions #TODO add commands to help  
	mPrint('FUNC', f'help()')
	rPrint('\nBenvenuto nella lista comandi,')
	rPrint('digita \'<comando> help\' per avere ulteriori informazioni\n')
	
	rPrint('   ----#Commandi principali#----')
	rPrint('        h -> Apre questo menu')
	rPrint('    start -> Fa partire un server')
	rPrint('     stop -> Ferma un server')
	rPrint('    reset -> Riavvia un server')
	rPrint('   backup -> backup help')
	rPrint('delbackup -> delbackup help')
	rPrint('    check -> is server alive?')
	rPrint('    abort -> will you use this?')
	rPrint('     back -> same as backup')
	rPrint('      end -> Ferma lo script')
	rPrint('     sync -> Sincronizza proprieta del server.')
	rPrint('       ls -> Mostra una lista dei server trovati')
	rPrint('      log -> Mostra i log nella console se attivo')
	rPrint('       ip -> Cabia l\'ip usato per i server')
	rPrint('     port -> Cambia la porta usata per i server')
	rPrint('     rcon -> Visualizza o aggiorna la porta rcon')
	rPrint('  ----#-------------------#----')

def inHelp(menu): #detailed command specific helps 
	mPrint('FUNC', f'inHelp({menu})')
	rPrint('\n\n')
	menu = str(menu)
	menu = menu.lower()
	if menu == 'start':
		rPrint('Fa partire un server:')
		rPrint(Fore.GREEN + '\tsyntax: start <server-id> [server-port]' + Fore.RESET)
		rPrint('| server-id: OBBLIGATORIO, ogni server rilevato ha un id associato, invia il comando \'ls\' per vedere gli id')
		rPrint('| server-port: OPZIONALE, porta numerica su cui il server rimane in ascolto per altri giocatori')

	elif menu == 'stop':
		rPrint('Ferma un server:')
		rPrint(Fore.GREEN + '\tsyntax: stop [server-id]' + Fore.RESET)
		rPrint('| server-id: OPZIONALE, se omesso verranno fermati tutti i server')
		rPrint('| ogni server rilevato ha un id associato, invia il comando \'ls -f\' per vedere gli id dei server online')

	elif menu == 'restart':
		rPrint('Riavvia un server:')
		rPrint(Fore.GREEN + '\tsyntax: restart [server-id]' + Fore.RESET)
		rPrint('| server-id: OPZIONALE, se omesso verranno riavviati tutti i server')
		rPrint('| ogni server rilevato ha un id associato, invia il comando \'ls -f\' per vedere gli id dei server online')

	elif menu == 'backup':
		rPrint('Comando utile al backup dei server:')
		rPrint(Fore.GREEN + '\tsyntax: backup <[all/online/list] / [server-id]>' + Fore.RESET)
		rPrint(Fore.GREEN + 'Alias: back' + Fore.RESET)
		rPrint('| Dato che la sintassi può risultare confusionale, ecco alcuni esempi')
		rPrint(f'| {Fore.YELLOW} backup all{Fore.RESET}: Crea un backup di tutti i server rilevati.')
		rPrint(f'| {Fore.YELLOW} backup online{Fore.RESET}: Crea un backup di tutti i server rilevati online.')
		rPrint(f'| {Fore.YELLOW} backup list{Fore.RESET}: Mostra una lista della cartella ./backup.')
		rPrint(f'| {Fore.YELLOW} backup <server-id>{Fore.RESET}: Crea il backup di un server specifico.')
		rPrint('| ogni server rilevato ha un id associato, invia il comando \'ls\' per vedere gli id dei server rilevati')

	elif menu == 'delbackup':
		rPrint('Elimina un backup:')
		rPrint(Fore.GREEN + '\tsyntax: delbackup <backup-id>' + Fore.RESET)
		rPrint('| Elimina la cartella <backup-id> selezionato')
		rPrint('| I <backup-id> sono alfabetici e possono essere trovati usando il comando "backup list"')

	elif menu == 'sync':
		rPrint('Sincronizza i file server.properties con i parametri scelti:')
		rPrint(Fore.GREEN + '\tsyntax: sync [param] [server-id]' + Fore.RESET)
		rPrint('| param: OPZIONALE, scegli il parametro da sincronizzare con tutti i file server.properties (es: server-ip)')
		rPrint('| server-id: OPZIONALE, scegli con quali server sincronizzare certi parametri, digita \'ls\' per vedere gli id')
		rPrint('|')
		rPrint('| param list:')
		rPrint('| ip / server-ip')
		rPrint('| port / server-port')
		rPrint('| rcon')
		rPrint('| xmx')

	elif menu == 'ip' or menu == 'server-ip':
		rPrint('Mostra o cambia l\'ip nel file "properties.ini":')
		rPrint(Fore.GREEN + '\tsyntax: ip [newIp]' + Fore.RESET)
		rPrint('| newIp: OPZIONALE, se usato cambia l\'ip del file properties.ini')
		rPrint('|')
		rPrint('|N.B. il file properties.ini è un file di lavoro, per aggiornare le modifiche con i server usa il comando \'sync\'')

	elif menu == 'port' or menu == 'server-port':
		rPrint('Mostra o cambia la porta nel file "properties.ini":')
		rPrint(Fore.GREEN + '\tsyntax: port [newPort]' + Fore.RESET)
		rPrint('| newPort: OPZIONALE, se usato cambia la porta del file properties.ini')
		rPrint('|')
		rPrint('|N.B. il file properties.ini è un file di lavoro, per aggiornare le modifiche con i server usa il comando \'sync\'')

	elif menu == 'end':
		rPrint('Chiude eventuali server aperti, fa un controllo e chiude lo script.')
		rPrint(Fore.GREEN + '\tsyntax: end' + Fore.RESET)

	elif menu == 'h':
		rPrint('Hai davvero bisogno di aiuto per il menù "aiuto"?')
		rPrint(Fore.GREEN + '\tsyntax: help' + Fore.RESET)

	elif menu == 'ls':
		rPrint('Mostra una lista di server compatibili:')
		rPrint(Fore.GREEN + '\tsyntax: ls [-o] [-f]' + Fore.RESET)
		rPrint('|')
		rPrint('| ls -o: lista dei server online')
		rPrint('| ls -f: lista del server online, se trova un server online, verifica che lo sia.')
		rPrint('| N.B. un server viene considerato compatibile se al suo interno ha un file chiamato "server.properties" OPPURE "config.yml" E uno "start.bat"')

	elif menu == 'rcon':
		rPrint('Mostra le impostazioni rcon')
		rPrint(Fore.GREEN + '\tsyntax: rcon [-s]' + Fore.RESET)

	elif menu == 'check':
		rPrint('Is Server Alive? check with')
		rPrint(Fore.GREEN + '\tsyntax: check [server-id]' + Fore.RESET)

	elif menu == 'sync':
		rPrint('Sincronizza il properties.ini su tutti i server')
		rPrint('Se il log è attivo crea un casino di log')
		rPrint('Dev use, non credo tu abbia bisogno di usarlo? devi farlo?')
		rPrint(Fore.GREEN + '\tsyntax: check [server-id]' + Fore.RESET)

	elif menu == 'abort':
		rPrint(Fore.GREEN + '\tsyntax: abort <[-f] / [-b]>' + Fore.RESET)
		rPrint('abort -f: chiude tutto dopo 5 secondi')
		rPrint('abort -b: fa un backup e chiude tutto')
		rPrint('Extreme use, non credo tu abbia bisogno di usarlo? devi farlo?')

	else:
		rPrint('Aiuti non trovati per questo comando...')

#runtime start#
#Preparazione (step 1)
try:
	createLog()

	if(os.path.isfile('properties.ini') == False): #works (checks if files are good)
		mPrint('INFO', '\nConfig file does not exist, creating one...')#why am I writing in different nations
		createConfig() # adds configs to config file
		mPrint('INFO', 'properties.ini creato, modificalo prima di avviare un server!')#sure idk
		crash() #brutal but works i guess
	else:
		if checkConfig() == 1:
			mPrint('INFO', 'Modifica l\'ip nel file properties.ini!')
			crash()
		config = ConfigObj('properties.ini')

		mPrint('INFO', 'Loading some properties...')
		log = config['log']
		log = False if log == 'False' else True

		devLogs = config['developer-logs']
		devLogs = False if devLogs == 'False' else True

		mPrint('INFO', f'cfglog: {config["log"]}')
		if(config['server-ip'] == '' or config['server-ip'].count('.')!=3 or not config['server-ip'].find('x') == -1): #kind of check if ip is good
			mPrint('FATAL', 'Questo non è un problema del codice, il file properties è errato, Hai impostato correttamente l\'ip?')
			crash()
		if(config['server-port'] == '' or config['server-port'].isnumeric() == False or int(config['server-port']) >= int(config['rcon-port'])): #kind of check if port is good
			mPrint('FATAL', 'Questo non è un problema del codice, il file properties è errato, Hai impostato correttamente la porta?')
			mPrint('INFO', 'Ricorda che la porta deve essere < rcon-port')
			crash()
		mPrint('INFO', 'Inizializzo lo starter con ip: '+ str(config['server-ip'])+':'+str(config['server-port']))

	mPrint('INFO', 'Se ci sono server online, usa il comando \'check help\' o \'set help\' per informazioni')

	mPrint('INFO', 'Loading server list...')
	loadServers()

	mPrint('INFO', 'Loading other properties...')
	maxBackupFolders = config['max-backup-folders']
	maxServers = int(config['rcon-port']) - int(config['server-port'])

except Exception:
	prtStackTrace(True)

#Inizio Console
rPrint('\n\n')
rPrint('| Benvenuto nel server starter!           |')
rPrint('| - Premi \'h\' per la lista dei comandi    |')
rPrint('| Creato da Latif                         |')
mPrint('INFO', f'| Puoi aprire {maxServers} server, usa \'info\' per informazioni')

#cmds: bottom of function
def main(run):
	global log
	print('>', end=' ')
	command = input().split(' ')
	logToFile('> ' + ' '.join(command))

	if len(command) == 2:# <cmd> help
		if command[1] == 'help':
			inHelp(command[0])
			return 0

	if command[0] == 'start':#
		if len(command) == 2:
			start(command[1])
		elif len(command) == 3:
			start(command[1], command[2])
		else:
			mPrint('WARN', 'non hai fornito nessun id server, "ls" per una lista, "server <id>" per farlo partire')

	elif command[0] == 'stop':#
		if len(command) ==  1:
			stop()
		elif len(command) == 2:
			stop(command[1])
		else:
			rPrint('Comando non riconosciuto, \'stop help\' per aiuto')

	elif command[0] == 'restart':#
		if len(command) ==  1:
			restart()
		elif len(command) == 2:
			restart(command[1])
		else:
			rPrint('Comando non riconosciuto, \'restart help\' per aiuto')

	elif command[0] == 'backup' or command[0] == 'back':#
		if len(command) >= 2:
			if command[1] == 'all':
				makeBackup(-1)
			elif command[1] == 'online':
				makeBackup()
			elif command[1] == 'list':
				if len(command) == 3:
					backList(int(command[2]))
				else:
					backList()
			else:
				try:
					#idToBack() = int(command[1])
					makeBackup(int(command[1]))
				except ValueError:
					mPrint('ERROR', 'Se hai provato ad inserire un ID, usane uno numerico.')
		else:
			rPrint('Comando non riconosciuto, \'backup help\' per aiuto')

	elif command[0] == 'delbackup':#
		try:
			delbackup(command[1])
		except IndexError:
			rPrint('Comando non riconosciuto, \'delbackup help\' per aiuto')

	elif command[0] == 'autobackup':	#autobackup: [time (minutes)] (folder auto\id) <-replace latest
		print(backup)
		print('')
		for x in backup:
			print(backup[x])
		if len(command) == 2:
			try:
				auto = int(command[1])
				return auto
			except ValueError:
				mPrint('WARN', 'Inserisci un valore numerico in minuti.')
		else:
			rPrint('Comando non riconosciuto, \'autobackup help\' per aiuto')

	elif command[0] == 'set': #specific for Dev use. no documentation lol noob:
		if len(command) == 3:
			set(command[1], command[2])
		else:
			mPrint('INFO', 'comando non riconosciuto, \'set help\'')

	elif command[0] == 'check':#
		if len(command) == 2:
			check(command[1])
		else:
			mPrint('INFO', 'comando non riconosciuto, \'check help\'')

	elif command[0] == 'sync':
		if len(command) == 1: #Sync all server
			rPrint('Vuoi sincronizzare i settings con tutti i server (Y/n): ')
			if yesNoInput(input()) == 'y':
				changeProperties('all')
				
		elif len(command) == 2: #Sync parameter
			try:
				tmp = changeProperties(command[1])
				if tmp == 69:
					mPrint('INFO', 'sync command error:')
			except Exception:
				mPrint('ERROR', ' La forma del comando è sbagliata??')
				prtStackTrace()

		elif len(command) == 3: #Sync parameter server-id
			try:
				tmp = changeProperties(command[1], int(command[2]))
				if tmp == 69:
					mPrint('INFO', 'sync command error:')
			except Exception:
				mPrint('ERROR', 'La forma del comando è sbagliata??')
				prtStackTrace()
			
		else:
			mPrint('ERROR', 'formato del comando errato.')

	elif command[0] == 'abort': #abort [-f] [-b]:
		if '-f' in command:
			abort(command[1])
		elif '-b' in command:
			abort(command[1])
		else:
			mPrint('INFO', 'comando non riconosciuto')

	elif command[0] == 'ip' or command[0] == 'server-ip':
		try:
			modIp(command[1])
			mPrint('INFO', 'Ip changed to ' + str(config['server-ip']))
			mPrint('DEV', 'Command: changing ip to '+str(config['server-ip']))

		except IndexError:
			mPrint('INFO', 'ip: '+str(config['server-ip']))
			mPrint('INFO', f'externalIp: {extIp}')

	elif command[0] == 'port' or command[0] == 'server-port':
		try:
			modPort(command[1])
			mPrint('INFO', 'Ip changed to ' + str(config['server-ip']))
			mPrint('DEV', 'Command: changing port to '+str(config['server-port']))

		except IndexError:
			mPrint('INFO', 'port: '+str(config['server-port']))	

	elif command[0] == 'rcon':
		try:
			if command[1] == '-s':
				rconSync()
		except IndexError:
			mPrint('INFO', f'rcon.port: {rconPort}, rcon.password: {rconPsw}')
			mPrint('WARN', 'DO NOT MANUALLY CHANGE THEM.') #wtfym fix this FIXME

	elif command[0] == 'log':
		log = False if log else True
		updateConfig('log', log)

		mPrint('INFO', 'log is now: ' + str(log))

	elif command[0] == 'end':
		#TODO 0 CHECK ARE THERE ONLINE SERVERS?
		crash()

	elif command[0] == 'h' or command[0] == 'help' or command[0] == '?':
		help()

	elif command[0] == 'xmx' or command[0] == 'ram':
		if len(command) == 1:
			mPrint('INFO', f'-Xmx: {config["-Xmx"]}')
		elif len(command) == 2:
			modRam(command[1])
		elif len(command) == 3:
			modRam(command[1], command[2])
		else:
			pass #Print help

	elif command[0] == 'ls':
		if len(command) == 1:
			ls()
		elif '-f' in command:
			printOnline(True)
		elif '-o' in command:
			printOnline()
		elif '-u' in command:
			loadServers()
		else:
			mPrint('WARN', 'Comando non riconosciuto.')

	elif command[0] == 'dev': #Works in IDLE shell
		mPrint('DEV', 'Entered IDLE dev mode.')
		return -2

	else:
		rPrint('Comando non riconosciuto, \'help\' per la lista comandi.')

	if not run:
		mPrint('INFO', 'Bye bye.')

	return 0

# -------- COMMANDS --------
# start <serverID> [port]	//serverID can be string
# stop <serverID> [port]	//serverID can be string
# restart <serverID>		//serverID can be string
# backup/back [cmd]			//cmd: serverID / all / online / list [serverID]
# delbackup <serverID> 		//ADD OPTIONS PLS
# autobackup [time (minutes)] (folder auto\id) <-replace latest //REVIEW
# set <serverID> <status>	//manually sets serverID to status (on/off line) USE check INSTEAD only test purposes
# check <serverID>			//pings server port to check if it's on
# sync [setting] [serverID]	//without params syncs everything to every server
# abort <-f/-b>				//-f: force -b: backup
# ip/server-ip [newIP]		//if no params: shows IP; else: sets newIP 
# port/server-port [newPort]//if no params: shows port; else: sets newPort
# rcon [-s]					//shows rcon params; -s: syncs rcon for some reason
# log						//Switches script log on/off
# end						//stops script
# h/help					//help
# xmx/ram [ram] <serverID>	//shows / changes xmx value; ex syntax: xmx 4G 2 | xmx 1024M
# ls [-f / -o / -u]			//-f: checks if servers are still online and lists them / -o lists allegedly online servers / -u reloads server list
# dev						//exits sctipt so you can call functions and shit (IDLE shell)

# -------- MAINLOOP --------
autoBack = False
seconds = 0 #autobackup (not yet implemented)
while run:
	try:
		resp = main(run)
		if resp == -2:
			break
		elif resp != 0:
			autoBack = True
			startTime = time.time()
			seconds = int(resp)*60
		elif resp == 0 and autoBack == True:
			autoBack = False
			mPrint('INFO', 'Il backup automatico è stato disattivato')

		if autoBack:
			backnames = autobackup()
			if backnames != 0:
				subprocess.Popen(["python", "zscripts\\autobackup.py"] + backnames, creationflags=subprocess.CREATE_NEW_CONSOLE)

	except Exception:
		prtStackTrace()
		print(f'Il manager è crashato, guarda il log per informazioni.')
		input('Premi invio per uscire')
		exit()


# __    __  __    __    _____    ____  _   _  ____  ___     ___  _____  ____  ____    ___  __  __  ___  _  _  ___ 
#(  )  (  \/  )  /__\  (  _  )  (_  _)( )_( )(_  _)/ __)   / __)(  _  )(  _ \( ___)  / __)(  )(  )/ __)( )/ )/ __)
# )(__  )    (  /(__)\  )(_)(     )(   ) _ (  _)(_ \__ \  ( (__  )(_)(  )(_) ))__)   \__ \ )(__)(( (__  )  ( \__ \
#(____)(_/\/\_)(__)(__)(_____)   (__) (_) (_)(____)(___/   \___)(_____)(____/(____)  (___/(______)\___)(_)\_)(___/ 
