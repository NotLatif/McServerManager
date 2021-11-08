try:
	import os
	import subprocess
	import time
	import keyboard
	import random
	import traceback
	import shutil
	import configobj
	import importlib.util
	import msvcrt
	from colorama import Fore, Back, Style, init
	from distutils.dir_util import copy_tree
	from configobj import ConfigObj
	from datetime import datetime
	from shutil import copyfile
	from zipfile import ZipFile 
	from mcrcon import MCRcon
	from requests import get
	from glob import glob
except ModuleNotFoundError:
	print('FATAL \n' + str(traceback.format_exc()))
	input('Premere invio per interrompere')

init()
print(Style.BRIGHT)

tellrawspec = importlib.util.spec_from_file_location("tellraw.py", "zscripts\\tellraw.py")
tellraw = importlib.util.module_from_spec(tellrawspec)
tellrawspec.loader.exec_module(tellraw)

autobackupspec = importlib.util.spec_from_file_location("tellraw.py", "zscripts\\autobackup.py")
AutoBackup = importlib.util.module_from_spec(autobackupspec)
autobackupspec.loader.exec_module(AutoBackup)

log = True
bmx = 15
rconPort = 25575
rconPsw = 'Rcon69Psw'
online = {}
#Dict of online server, strcuture: {onlineId: ['Server', state, port, rcon]}; state can be: 0:offline, 1:online, 2:restarting

run = True
now = str(datetime.now().strftime('%d-%m-%Y_%H_%M_%S'))
logNow = str(datetime.now().strftime('%Y-%m-%d_%H_%M_%S'))
logFile = str(f'logs\\{logNow}.txt') 

extIp = get('https://api.ipify.org').text

back = {}
#back{id: [aaId, date, [IDs]}


def prtStackTrace(Fatal = False):
	if Fatal:
		mPrint('FATAL', '\n' + traceback.format_exc())
		global run
		run = False
	else:
		mPrint('ERROR', '\n' + traceback.format_exc())

def createLog():
	if not os.path.exists('logs'): #crea la dir log se non esiste
		os.mkdir('logs')
	if not os.path.isfile(logFile): #crea il file logs\{now} se non esiste
		data = 'Welcome to the log lmao nothing useful here? Probabli not.\n'
		data = data + 'I present to you the complete mess of this script\n\n'
		writeDataFile(logFile, data) #first commit
	else:
		mPrint('FUNC', f'createLog()') #log file exists??? wtf how (impossible)
		mPrint('DEV', f'File già presente: {logFile}') #actually too scared to delete this who knows

def logToFile(newdata):
	File = getDataFile(logFile)
	File = File + str(newdata) + '\n'
	writeDataFile(logFile, File)

def yesNoInput(input):
	input = input.lower()
	if (input == 'y' or input == '' or input == 'yes'):
		return 'y'
	else:
		return 'n'

def rPrint(text, reqlog=False):
	mPrint(text, '', reqlog, True)

def mPrint(prefix, text='', reqlog=False, raw=False):
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

def checkConfig():
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

def createConfig(): #works but remember to update OHSHIT FORGOT
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

def updateConfig(key, value): #worked last time I checked
	mPrint('FUNC', f'updateConfig({key}, {value})')
	config[key] = value
	config.write()
	remQuote('properties.ini')
	
def crash(): #lol does it work if it crashes the program? (yes because it just stops it)
	mPrint('FUNC', f'crash()')
	mPrint('Premere un tasto per terminare...')
	input()
	exit()

def remQuote(file):#just works (all the three things)
	data = getDataFile(file) #apre e prende i dati
	data = data.replace('"','') #toglie gli "
	writeDataFile(file, data) #apre e riscrive i dati
def getDataFile(file): #apre file e prende i dati
	file = open(file, "rt")
	data = file.read()
	file.close()
	return data
def writeDataFile(file, data): 
	file = open(file, "wt")
	file.write(data)
	file.close()

def verifyStatus(server):
	mPrint('FUNC', f'verifyStatus({server})')
	if server < 0:
		pass
	else:
		if server <= len(online):
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
					if isServerAlive(config['server-ip'], online[server][2]):
						mPrint('INFO', f'Server: {online[server][0]} è stato rilevato. ({round(currentTime-beginTime)}sec.)')
						online[server][1] = 1
						break
					else:
						mPrint('INFO', 'Offline.')
						mPrint('INFO', 'Riprovo tra 10 secondi...')
					startTime = time.time()
				try:
					if keyboard.is_pressed('q'):
						online[server][1] = 1
						mPrint('WARN', f'Questo server ora risulterà online.')
						mPrint('INFO', f'Usa il comando \'stop {server}\' se vuoi farlo risultare offline.')
						break
				except:
					pass
		else:
			mPrint('ERROR', 'Server non trovato.')

def loadServers(): 
	mPrint('FUNC', f'loadServers()')
	s = dirGrab()
	x = 0
	for server in s:
		#proprietà dei server.properties
		sPort = getProperty('server-port', server)
		rPort = getProperty('rcon.port', server)
		if sPort < 0:	# FIXME 1 (CHECKME) [non dovrei prendere dall'ini??? perché questi valori fissi??]
			mPrint('ERROR', f'valore server-port non valido nel server: {server}')
			mPrint('INFO', 'porto la server-port a 25565.') ##Ma perché proprio 25565??
			sPort = 25565
		if sPort >= 25575:
			mPrint('WARN', f'server: {server} ha una porta >= a 25575.')
			mPrint('INFO', 'per evitare problemi porto la server-port a 25565.')
			sPort = 25565
		online[x] = [str(server), 0, sPort, rPort] #technically offline but ok 
		x += 1
	mPrint('INFO', f'Loaded {x} servers.')

	mPrint('INFO', 'Imposto automaticamente le porte rcon dei server.')
	changeProperties('all', -1, False)
	rconSync()
	batFixer(-1, config['-Xmx'])
	backSync()

def batter(i, batCopy, server, s):
	mPrint('FUNC', f'batter({i}, {batCopy}, {server}, {s})')
	batPaste = batCopy
	
	path = s[i] + '\\start.bat'
	if not os.path.isfile(path):
		mPrint('IMPORTANT', f'IL FILE {path} NON ESISTE, IO TE LO FACCIO MA VEDI CHE IL .jar È SCRITTO server.jar QUINDI ATTENTO CHE SIA GIUSTO SENNO NON PARTE IL SERVER OK?')
		try:
			data = getDataFile('zscripts\\start.bat')
			writeDataFile(path, data)
		except FileNotFoundError:
			writeDataFile('zscripts\\start.bat', 'for fuck\'s sake don\'t delete me')
			data = getDataFile('zscripts\\start.bat')
			writeDataFile(path, data)

	if log:
		mPrint('WORK', f'batFixer server: {s[i]}')
		mPrint('WORK', f'start.bat path: {path}')
			
	jarFile = getDataFile(s[i]+'\\start.bat')
	File = jarFile.split(' ')

	mPrint('DEV', File)
	for x in range(len(File)):
		if '.jar' in File[x]:
			jarFile = File[x]
			break
		else:
			jarFile = 'server.jar'
			
	batPaste = batCopy.replace('*JARFILE*', jarFile)
	batPaste = batPaste.replace('*PATH*', s[i])
	writeDataFile(path, batPaste)
	mPrint('DEV', 'batcopy: '+batPaste)

def batFixer(server, xmx = None):
	mPrint('FUNC', f'batFixer({server}, {xmx})')
	#gets raw data and make raw bat file (and sends it to batter())
	if xmx == None:
		xmx = config['-Xmx']

	s = dirGrab()

	placeholder = 'zscripts\\placeholder.bat'
	try:
		batCopy = getDataFile(placeholder)
	except FileNotFoundError:
		newPlaceholder = 'cd *PATH*\njava *MaxHeap* -jar *JARFILE* nogui'
		writeDataFile(placeholder, newPlaceholder)
		batCopy = getDataFile(placeholder)

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

	batCopy = batCopy.replace('*MaxHeap*', f'-Xmx{xmx}M')

	if server == -1:
		for i in range(len(s)):
			batter(i, batCopy, server, s)	
	else:
		i = server
		batter(i, batCopy, server, s)

def getProperty(key, server): #pull and return info from server.properties files
	mPrint('FUNC', f'getProperty({key}, {server})')
	key = str(key)
	path = server + '\\server.properties'
	temp_cfg = ConfigObj(path)
	if key in temp_cfg:
		return int(temp_cfg[key])
	else:
		return -1

def startChangeProperties(key, value, serverid):#what is this even supposed to do
	mPrint('FUNC', f'startChangeProperties({key}, {value}, {serverid})')
	paths = dirGrab()
	server = paths[int(serverid)]
	server = server + '\\server.properties'
	temp_cfg = ConfigObj(server)
	temp_cfg[key] = int(value)
	temp_cfg.write()
	remQuote(server)

def rconSync(rconPort=25575):#param is starting port
	mPrint('FUNC', f'rconSync({rconPort})')
	if rconPort < 25575:
		mPrint('WARN', f'rcon.port è impostato a {rconPort}')
		mPrint('WARN', f'per prevenire problemi con le porte usate dai server')
		mPrint('WARN', f'Impostare un numero maggiore/uguale a 25575.')
		mPrint('WARN', f'Tenere in considerazione le porte utilizzate per tenere i server online.')
		return -1

	for i in range(len(online)):
		if online[i][1] != 0:
			mPrint('ERROR', 'Ho rilevato un server online,')
			mPrint('WARN', 'per evitare problemi chiudi tutti i server con il comando \'stop\'')
			mPrint('WARN', 'se credi sia un errore aggiorna la lista server online usando il comando \'ls -f\'')
			mPrint('WARN', 'anche il comando \'set help\' potrebbe aiutarti')
			return -2

	mPrint('INFO', 'rcon.port sync')
	mPrint('DEV', f'rconSync(rconPort={rconPort})')
	s = dirGrab()


	x = 0
	for server in s:

		path = server + '\\server.properties'
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
				if not 'rcon.port' in temp_cfg:
					temp_cfg['rcon.password'] = rconPsw
				temp_cfg.write()
				remQuote(path)
			x+=1

def workChangeProperties(key, name):#it worked on my machine
	mPrint('FUNC', f'workChangeProperties({key}, {name})')
	name = name + '\\server.properties'
	temp_cfg = ConfigObj(name)
	
	mPrint('DEV', f'name:{name}')

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
		for i in range(len(online)):
			batFixer(i, config['-Xmx'])
		return 0
	if key == 'all':
		temp_cfg['server-ip'] = config['server-ip']
		temp_cfg['server-port'] = config['server-port']
		mPrint('INFO', 'changed ip and port to: ' + config['server-ip'] + ":" + str(config['server-port']) + ' for server: '+str(name))
	else:
		temp_cfg[str(key)] = config[str(key)]
		mPrint('INFO', 'server: '+ str(name))
		mPrint('INFO', 'changed key: ' + key + ", to value:" + temp_cfg[key])
	temp_cfg.write()

	#chiama remQuote per togliere i '"'
	remQuote(name)
			
def changeProperties(key, server=-1, syncRcon=True):#key = property name
	mPrint('FUNC', f'changeProperties({key}, {server})')
	mPrint('INFO', 'key: ' + str(key))

	dirs = dirGrab()
	#initial parse
	if (key != 'ip' and key != 'server-ip' and key != 'port' and key != 'server-port' and key != 'all' and key != 'ram' and key != 'xmx' and key != '-Xmx'):
		mPrint('ERROR', 'key error.')
		return 69

	if server < 0: #cambia tutti i server
		mPrint('DEV', 'All servers')
		for name in dirs:
			workChangeProperties(key, name)
			if syncRcon:
				rconSync()
	else: #cambia il server scelto
		mPrint('DEV', f'Server {server}')
		workChangeProperties(key, dirs[int(server)])
		if syncRcon:
			rconSync()
	return 0

def changeSingleProperty(key, value, name):
	mPrint('FUNC', f'singleChangeProperties({key}, {value}, {name})')
	name = name + '\\server.properties'
	temp_cfg = ConfigObj(name)
	mPrint('DEV', f'name:{name}')

	temp_cfg[key] = value
	temp_cfg.write()
	remQuote(name)

	mPrint('INFO', 'server adapted: '+ str(name))
	mPrint('DEV', 'changed key: ' + key + ", to value:" + value)

#Runtime config modifiers
def modIp(newIp, sync=True):#should work
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


def modPort(newPort, sync=True):#should work
	mPrint('FUNC', f'modPort({newPort}, {sync})')
	if not (newPort == '' and newPort.isnumeric() == False and int(newPort) >= 0):
		if newPort >=25575:
			mPrint('ERROR', 'server-port can\'t be >= than 25575.')
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


def modRam(xmx, server=-1):
	if not str(server).replace('-', '').isnumeric():
		server = txtToId(server)

	server = int(server)
	
	if not('G' in str(xmx) or 'M' in str(xmx)):
		mPrint('ERROR', 'Invalid -Xmx format, \'xmx help\'')
		return -1

	if server == -1:
		updateConfig('-Xmx', xmx)

		for i in range(len(online)):
			batFixer(i, xmx)
	elif server < len(online):
		batFixer(server, xmx)
	else:
		mPrint('ERROR', 'Server non trovato!')

############################################################################
def isServerAlive(ip, port):#works
	mPrint('FUNC', f'isServerAlive({ip}, {port})')
	import socket
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		return s.connect_ex((ip, port)) == 0

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

def ls(): #works it just goes BRRR OUTPUT
	mPrint('FUNC', f'ls()')
	dirs = dirGrab()
	count = 0
	rPrint('------Server Trovati------')
	rPrint('Green = Online')
	for x in range(len(dirs)):
		if online[x][1] == 1:
			pre = Fore.GREEN
			aft = online[x][2]
		else:
			pre = Fore.RESET
			aft = ''
		rPrint(f'{pre}{x}|-> {online[x][0]} {aft}{Fore.RESET}')
		count += 1
	print('\n')

def listOnline(check=False):
	mPrint('FUNC', f'listOnline({check})')

	onList = []

	for i in range(len(online)):
		if online[i][1] != 0:
			onList.append(i)
			mPrint('INFO', f'Found online server: {online[i][0]}')
			mPrint('DEV', f'Server info, id: {i}, state: {online[i][1]}, port: {online[i][2]}, rcon: {online[i][3]}')
	if check:
		for i in range(len(online)):
			if online[i][1] != 0:
				if isServerAlive(config['server-ip'], online[i][2]):
					online[i][1] = 1
					mPrint('DEV', f'found True Online Server {online[i][0]} with id: {i}, is now in state {online[i][1]}')
				else:
					online[i][1] = 0
					onList.remove(i)
					mPrint('DEV', f'found False Online Server {online[i][0]} with id: {i}, is now in state {online[i][1]}')
	return onList

def printOnline(check=False):
	mPrint('FUNC', f'printOnline({check})')
	onlineServers = listOnline(check)
	rPrint('------Server Online------')
	rPrint(f'{config["server-ip"]} | {extIp}')
	if len(onlineServers) == 0:
		rPrint(' |-> No online server found.')
		rPrint(' |-> GOOD')
	else:
		for x in onlineServers:
			rPrint(str(x) + '|-> ' + online[x][0] + ', ' + str(online[x][2]))
	print('\n')


def sendRcon(server, command, text = None):
	mPrint('FUNC', f'sendRcon({server}, {command}, {text})')

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
	mPrint('DEV', f'attempting rcon communication, \n\tserver: {server}\n\tcommand: {command}\n\ttext: {text}\n\tsend: {send}')
	mPrint('DEV', f'connection informations: \n\tip: {config["server-ip"]}\n\tpsw: {rconPsw}\n\tport: {online[server][3]}')

	try:
		with MCRcon(config['server-ip'], rconPsw, online[server][3]) as mcr:
			resp = mcr.command(send)
			mPrint('RESP', 'server resp: ' + resp)
	except ConnectionRefusedError:
		mPrint('INFO', 'I think some error occured? I\'ll just log it lol')
		mPrint('DEV', traceback.format_exc())
	except Exception:
		prtStackTrace()

def start(server, port=None):#I hope it works
	mPrint('FUNC', f'start({server}, {port})')
	server = str(server)

	#Preparation
	try: #If server is literal ('Server1') change to id, else cast int jtbs
		server = int(server)
	except ValueError:
		mPrint('WORK', 'Server is literal, scanning for id')
		server = txtToId(server)
		
	if server != -1:
		mPrint('WORK', 'found server id: ' + str(server))
	else:
		mPrint('ERROR', 'Server non trovato :(')
		return -1

	if port is None:
		port = int(config['server-port'])
	else:
		mPrint('INFO', 'running on custom server port: ' + str(port))
		port = int(port)
		startChangeProperties('server-port', port, server)

	s = dirGrab()
	#Start
	if server >= len(online):
		mPrint('WARN', f'Il server {server} non esiste, ho rilevato solo {len(online)} server')
		mPrint('INFO', 'Il comando \'ls -u\' aggiorna la lista server!')
		return -1

	for i in range(len(online)):
		if s[server] in online[i] and online[i][1] != 0: #Controllo se il server che sto facendo partire è già online
			mPrint('INFO', 'Controllo lo stato del server...')
			if isServerAlive(config['server-ip'], port):
				mPrint('WARN', 'Server già partito, annullo il comando')
				mPrint('WARN', 'La porta ' + config['server-ip'] +':'+str(port) + ' è attualmente occupata. Impossibile startare un server')
				return -1
			else:
				mPrint('INFO', f'Server segnalato online in realtà è offline, aggiorno lo stato per il server {server}')
				online[i][1] = 0

		if port in online[i] and online[i][1] != 0: #Controllo se la porta è libera
			mPrint('INFO', 'Controllo lo stato del server...')
			if isServerAlive(config['server-ip'], port):
				mPrint('WARN', f'Esiste un server online su questa porta: {port}')
				mPrint('INFO', 'Provo con le prossime 5 porte...')
				starterP = port
				for y in range(1, 5): #Provo le prossime 5 per qualche motivo
					yPort = port+y
					if isServerAlive(config['server-ip'], yPort):
						mPrint('INFO', f'{yPort} non disponibile.')
					else:
						mPrint('INFO', f'Porta {yPort} libera, uso questa.')
						port = yPort
						break
				if port == starterP:
					mPrint('WARN', f'Nessun server trovato su 6 porte a partire da {starterP}')
					return 0

	mPrint('WORK', f'building server path for server id <{str(server)}>')
	file = s[server]+r'\start.bat'
	mPrint('WORK', f'builded path for {str(s[server])} ({file})')

	if port != config['server-port']:
		mPrint('DEV', f'if port != {config["server-port"]}: True')
		changeSingleProperty('server-port', str(port), s[server])

	try:
		p = subprocess.Popen(file, creationflags=subprocess.CREATE_NEW_CONSOLE)
		mPrint('INFO', 'Server initialized.')
		online[server][1] = 3 #[name,STATE,port,rcon]
		online[server][2] = port

		mPrint('INFO', 'Verifico lo stato del server...')
		verifyStatus(server)
		mPrint('INFO', 'Condividi il tuo ip per far entrare anche gli altri!')
		if port != '25565':
			mPrint('INFO', f'{extIp}:{port}')
		else:
			mPrint('INFO', f'{extIp}')

	except Exception:
		mPrint('ERROR', 'C\'è stato un problema: printing Traceback:')
		prtStackTrace()

def stop(server = None, Force = False):
	mPrint('FUNC', f'stop({server})')

	#preparazione
	try:
		if server.isnumeric() == False:
			mPrint('WORK', 'Server is not numeric')
			server = txtToId(server)
			mPrint('WORK', f'server = {server}')
	except AttributeError:
		mPrint('WORK', 'Server is numeric')
		server = int(server)

	if server is None: #no input -> online/check if multiple are on
		mPrint('WORK', 'Server is None')
		count = 0
		for i in range(len(online)):
			if online[i][1] == 1:
				count += 1
		if count == 1:
			for i in range(len(online)):
				if online[i][1] == 1:
					server = i
		elif count == 0:
			mPrint('INFO', 'Nessun server trovato online!, \'ls help\'')
			return -1
		else:
			mPrint('INFO', 'Piú di un server trovato online.')
			server = -1
		mPrint('WORK', f'server = {server}')

	if server == -1: #Multiple servers are online, but are they really?
		mPrint('WORK', 'Checking all servers')
		#force online list to be true online
		for x in range(len(online)): # online[onlineId] = [server, state, port, rcon]
			if online[x][1] == 1:#online?
				if not isServerAlive(config['server-ip'], online[x][2]):
					online[x][1] = 0
					mPrint('WORK', f'server {x} was fake online')
			if not isServerAlive(config['server-ip'], online[x][3]):
				mPrint('FATAL', f'La porta rcon per il server {x} non è in ascolto, sarà impossibile chiudere questo server.')
		
		for x in range(len(online)):
			if(online[x][1]):
				try:
					splash = getSplash('stop')
					sendRcon(x,'tellraw @a', str(tellraw.make(text=splash, color='green', bold=True)))
				except Exception:
					prtStackTrace()
	else: # only one server is online
		mPrint('WORK', 'Checking one server')
		if isServerAlive(config['server-ip'], online[server][2]) == False:
			online[server][1] = 0
			mPrint('WARN', f'Il server {online[server][1]} è in realtà offline. annullo il comando')
			return -1

		if isServerAlive(config['server-ip'], online[server][3]) == False:
			mPrint('FATAL', f'La porta rcon per il server {online[server][0]} non ascolta. annullo il comando.')
			return -1

		try:
			splash = getSplash('stop')
			sendRcon(server,'tellraw @a', str(tellraw.make(text=splash, color='green', bold=True)))
		except Exception:
			prtStackTrace()

	mes = str(tellraw.make(text='Server is going bye bye, confirm in python script pls', color='red', bold=True))

	#those send
	if server < 0: #-1| target all online server
		for x in range(len(online)):
			if online[x][1] == 1:
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
		for x in range(len(online)):
			if online[x][1] == 1:
				try:
					mPrint('INFO', 'mando una richiesta al server...')
					sendRcon(x, 'stop')
					online[x][1] = 0
				except Exception:
					prtStackTrace()
			else:
				mPrint('INFO', f'Il server {online[x][0]} è già offline')
				mPrint('INFO', f'Aggiorno le impostazioni...')
				online[x][1] = 0
				mPrint('INFO', 'Fatto!')
				mPrint('DEV', f'online[x][1] is now: {online[x][1]}')
	else: # only target one server
		if server >= len(online):
			mPrint('WARN', f'Il server {server} non esiste, ho rilevato solo {len(online)} server')
			mPrint('INFO', 'Il comando \'ls -u\' aggiorna la lista server!')
		else:
			if online[server][1] == 1:
				sendRcon(server, 'tellraw @a', mes)
				if not Force:
					mPrint('WARN', 'Do you want to stop the server?')
					command = yesNoInput(input('(Y/n) > '))
					logToFile('> ' + command)
				else:
					command = 'y'

				if command == 'y':
					try:
						mPrint('INFO', 'mando una richiesta al server...')
						sendRcon(server, 'stop')
						online[server][1] = 0
					except Exception:
						prtStackTrace()
				else:
					mPrint('INFO', 'Comando stop annullato')
					mPrint('INFO', f'Il server {online[server][0]} è ancora online.')
					return -2

			else:
				mPrint('INFO', f'Il server {online[server][0]} è già offline')
				mPrint('INFO', f'Aggiorno le impostazioni...')
				online[server][1] = 0
				mPrint('INFO', 'Fatto!')
				mPrint('DEV', f'online[server][1] is now: {online[server][1]}')
				return -1

def restart(server = None):#not yet
	mPrint('FUNC', f'restart({server})')

	if server == None:
		mPrint('INFO', 'Provo a riavviare tutti i server.')
		stopping = []
		for x in range(len(online)):
			if online[x][1] == 1:
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
			online[x][1] = 2
		for x in range(len(stopping)):
			start(x)

	else:
		if str(server).isnumeric():
			server = int(server)
		else:
			server = txtToId(server)
			if str(server).isnumeric():
				mPrint('ERROR', 'Server non trovato.')

		mPrint('INFO', f'Provo a riavviare il server {server}.')

		try:
			stop(server, True)
			online[server][1] = 2
			time.sleep(5) ##FIXME <<<<<<<<<< maybe get a return from rcon?? IDK MAYBE MULTITHREADING!!!!
			start(server)
		except Exception:
			prtStackTrace()

def txtToId(txt):
	mPrint('FUNC', f'txtToId({txt})')
	i = 0 
	for x in dirGrab():
		if x == txt:
			mPrint('WORK', f'returning: {i}')
			return i
		i+=1
	return -1

def set(server, param, value = None):
	mPrint('FUNC', f'set({server}, {param}, {value})')
	mPrint('WARN', 'Usare questa funzione solo se necessario.')
	s = dirGrab()
	if value != None: #raw from comand
		online[server][param] = value
		return 0

	if str(param).isnumeric():
		if int(param) == 1:
			param = 'online'
		elif int(param) == 0:
			param = 'offline'
	param = param.lower()
	try: #from program
		if not str(server).isnumeric():
			for x in range(len(online)):
				if s[x] == server:
					server = x
					break
				else:
					server = None
			if server == None:
				print('ERROR', 'Nessun server trovato, prova con un id! \'ls\'')
				return -1

		server = int(server)
		if not str(param).isnumeric():
			if param == 'online':
				online[server][1] = 1
				mPrint('INFO', f'Il server {online[server][0]} ora risulta online.')
			elif param == 'offline':
				online[server][1] = 0
				mPrint('INFO', f'Il server {online[server][0]} ora risulta offline.')
	except Exception:
		prtStackTrace()

def check(param, port=0): #Add command 'check [port|id|-f]' default: 25565 checks if server is online and updates online{}
	mPrint('FUNC', f'check({param}, {port})')
	try:
		param = int(param)
	except Exception:
		param = txtToId(param)

	if param < 1000 and param >= 0:
		if param >= len(online):
			mPrint('Server non trovato, \'ls -u\' per aggiornare la lista')
			return -1
		if port == 0:
			if isServerAlive(config['server-ip'], online[param][2]):
				mPrint('INFO', 'Server is online.')
				online[param][1] = 1
				return 1
			else:
				mPrint('INFO', 'Server is offline')
				online[param][1] = 0
				return 0
		else:
			if isServerAlive(config['server-ip'], port):
				mPrint('INFO', 'Server is online.')
				online[param][1] = 1
				online[param][2] = port
				return 1
			else:
				mPrint('INFO', 'Server is offline')
				online[param][1] = 0
				return 0
	else:
		if isServerAlive(config['server-ip'], param):
			mPrint('INFO', 'Un server è attivo su questa porta.')
			mPrint('INFO', 'Provvedo a sincronizzarlo per te, ma devi darmi l\'id del server!')
			ls()
			
			while True:
				s = input('[id]> ')
				if check(s) != -1:
					if not isServerAlive(config['server-ip'], online[s][3]):
						mPrint('ERROR', 'La porta rcon non è disponibile, perfavore riavvia il server per evitare problemi.')
					else:
						break
		else:
			mPrint('INFO', f'Nessun server è attivo sulla porta {param}!')
			
def getSplash(menu = 'default'):
	if menu == 'default':
		lst = 'zscripts\\spl\\splashes.txt'
	elif menu == 'stop':
		lst = 'zscripts\\spl\\stopSplashes.txt'
	elif menu == 'backup':
		lst = 'zscripts\\spl\\backSplashes.txt'
	lst = getDataFile(lst)
	d = lst.split('\n')
	return random.choice(d)

def abort(method):
	mPrint('FUNC', f'abort({method})')
	if method == '-f':
		mPrint('IMPORTANT', 'You have 5 seconds to save everything')
		time.sleep(5)
		os.system('shutdown /s /t 1')
	elif method == '-b':
		backup(-1)
		os.system('shutdown /s /t 1')

def backList(server = -1): 
	mPrint('FUNC', f'backList()')
	backSync()
	rPrint(f'{Fore.GREEN}|------Backups------\n8{Fore.RESET}')
	if server == -1:
		for i in range(len(back)):
			rPrint('|')
			rPrint(f'{Fore.MAGENTA}|->{back[i][1]}{Fore.RESET} (ID: {back[i][0]})')
			for j in range(len(back[i][2])):
				rPrint(f'{Fore.MAGENTA}|{Fore.RESET}|({j})-> {back[i][2][j]}')
	else:
		for i in range(len(back)):
			if online[server][0] in back[i][2]:
				rPrint('|')
				rPrint(f'{Fore.MAGENTA}|->{back[i][1]}{Fore.RESET} (ID: {back[i][0]})')
				rPrint(f'{Fore.MAGENTA}|{Fore.RESET}|({i})-> {online[server][0]}')
	rPrint(f'{Fore.GREEN}|-------------------\n8{Fore.RESET}')


def backSync():
	mPrint('FUNC', f'backSync()')
	if not os.path.exists('backups'):
		os.mkdir('backups')
		mPrint('INFO', 'Created backup directory.')
		
	folder = os.listdir(".\\backups")
	x = 0
	
	back.clear()

	for i in range(len(folder)):
		sub = os.listdir(f".\\backups\\{folder[x]}")
		if len(sub) == 0:
			shutil.rmtree(f'backups\\{folder[x]}')
			folder = os.listdir(".\\backups")
			mPrint('WORK', 'Cartella vuota.')
		else:
			back[x] = [num_string(i+1), folder[x], sub]
			mPrint('WORK', f'[{num_string(x)}, {folder[x]}, {sub}]')
			x+=1

def rconSave(server):
	sendRcon(server, 'save-all')

def backup(server=-2): #-1: all; -2:online
	mPrint('FUNC', f'backup({server})')
	now = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
	if not os.path.exists('backups'):
		os.mkdir('backups')
		mPrint('INFO', 'Created backup directory.')
	if server==-1: #all
		for i in range(len(online)):
			if online[i][1] == 1:
				if not (isServerAlive(config['server-ip'], online[i][2])):
					mPrint('WARN', 'Un server segnalato online è in realtà offline. Aggiorno la lista e creo un backup')
					online[i][1] = 0
					
			backup(i)
	elif server==-2: #online
		for i in range(len(online)):
			if online[i][1] == 1:
				if isServerAlive(config['server-ip'], online[i][2]):
					backup(i)
				else:
					mPrint('WARN', f'Il server "{online[i][0]}" è segnalato online ma risulta offline. Lo imposto come server offline.')
					online[i][1] = 0
	else:
		if not(server >= 0 and server <= len(online)):
			mPrint('WARN', f'Server {server} non trovato.')
			return -1

		now = datetime.now().strftime('%d-%m-%Y, %H_%M')

		if os.path.exists(f'backups\\{now}\\{online[server][0]}'):
			mPrint('ERROR', 'Hai creato un backup meno di un minuto fa!') #FIXME 3
		else:

			if online[server][1] == 1:
				if isServerAlive(config['server-ip'], online[server][2]):
					splash = getSplash('backup')
					sendRcon(server,'tellraw @a', str(tellraw.make(text=splash, color='yellow', bold=True)))
					rconSave(server)
			
			for i in range(len(back)):
				if (int(now[-2:]) - 1 == int(back[i][1][-2:])) and (now[:-2] == back[i][1][:-2]):
					if os.path.exists(f'backups\\{back[i][1]}\\{online[server][0]}'):
						backDir = f'backups\\{now}\\{online[server][0]}'
						break
					else:
						backDir = f'backups\\{back[i][1]}\\{online[server][0]}'
						break
				else:
					backDir = f'backups\\{now}\\{online[server][0]}'


			if len(back) == 0:
				backDir = f'backups\\{now}\\{online[server][0]}'

			try:
				os.mkdir(f'backups\\{now}')
			except FileExistsError:
				pass

			nFolders = next(os.walk('backups'))[1]
			if len(nFolders) > int(config['max-backup-folders']):
				n = len(nFolders) - int(config['max-backup-folders'])
				for i in range(n):
					nFolders = next(os.walk('backups'))[1]
					rem = min(nFolders)
					path = f'backups\\{rem}'
					shutil.rmtree(path)
					mPrint('WARN', 'Il numero di backup supera il limite, elimino le cartelle in più')

			os.mkdir(backDir)
			
			copy_tree(online[server][0], backDir)


			mPrint('INFO', f'Fatto ({online[server][0]})')

			backSync()

def autobackup(): #FIXME 3
	backNames = []
	''' UNCOMMENT THIS LATER
	for i in range(len(online)):
		if online[i][1] == 1:
			if isServerAlive(config['server-ip'], online[i][2]):
				backNames.append(online[i][0])
	if len(backNames) <= 0:
		mPrint('WARN', 'Nessun server rilevato online, autobackup funziona solo per i server online.')
		return 0
	else:
		return backNames
	'''
	for i in range(len(online)):
		backNames.append(online[i][0])
	return backNames


def delbackup(backupID = None):
	mPrint('FUNC', f'delbackup({backupID})')
	backSync()

	try:
		int(backupID)
	except ValueError:
		backupAA = backupID
		for i in range(len(back)):
			if back[i][0] == backupAA:
				backupID = i
	else:
		backupID = int(backupID)


	nServer = len(back[backupID][2])
	mPrint('WARN', f'Sei sicuro di voler eliminare il backup del giorno {back[backupID][1]}?')
	mPrint('WARN', 'QUEI DATI ANDRANNO PERSI PER SEMPRE (un sacco di tempo)')
	
	if input('(Y/N)> ').lower() == 'y':
		logToFile('(Y/N)> Y')
		path = 'backups\\' + back[backupID][1]
		try:
			shutil.rmtree(path)
		except FileNotFoundError:
			pass
	backSync()



def restorebackup(server):
	mPrint('FUNC', f'restorebackup({server})')
	pass


def num_string(n):
	string = ""
	while n > 0:
		n, remainder = divmod(n - 1, 26)
		string = chr(65 + remainder) + string
	return string.lower()


def help(): #works but remember to update 
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

def inHelp(menu): 
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
		if(config['server-port'] == '' or config['server-port'].isnumeric() == False or int(config['server-port']) >= 25575): #kind of check if port is good
			mPrint('FATAL', 'Questo non è un problema del codice, il file properties è errato, Hai impostato correttamente la porta?')
			mPrint('INFO', 'Ricorda che la porta deve essere < 25575')
			crash()
		mPrint('INFO', 'Inizializzo lo starter con ip: '+ str(config['server-ip'])+':'+str(config['server-port']))

	mPrint('INFO', 'Se ci sono server online, usa il comando \'check help\' o \'set help\' per informazioni')

	mPrint('INFO', 'Loading server list...')
	loadServers()

	mPrint('INFO', 'Loading other properties...')
	bmx = config['max-backup-folders']


except Exception:
	prtStackTrace(True)

#Inizio Console
rPrint('\n\n')
rPrint('| Benvenuto nel server starter!           |')
rPrint('| - Premi \'h\' per la lista dei comandi    |')
rPrint('| Creato da Latif\u2122 Co., Ltd.              |')

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
				backup(-1)
			elif command[1] == 'online':
				backup()
			elif command[1] == 'list':
				if len(command) == 3:
					backList(int(command[2]))
				else:
					backList()
			else:
				try:
					#idToBack() = int(command[1]) FIXME 0
					backup(int(command[1]))
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
			rPrint('Vuoi sincronizzare i settings con tutti i server (Y/N): ')
			if input().lower() == 'y':
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
		#TODO 0 CHECK ONLINE
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
#Commands: start, sync, ip | server-ip, port | server-port, rcon, log, end, h, ls; online, set

crashcount = 0
autoBack = False
seconds = 0 
while run:
	maxCrashes = 4
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
		if crashcount > maxCrashes:
			prtStackTrace()
			print(f'Il manager è crashato {crashcount} volte, guarda il log per informazioni.')
			input('Premi invio per uscire')
			exit()
		else:
			prtStackTrace()
			continue


# __    __  __    __    _____    ____  _   _  ____  ___     ___  _____  ____  ____    ___  __  __  ___  _  _  ___ 
#(  )  (  \/  )  /__\  (  _  )  (_  _)( )_( )(_  _)/ __)   / __)(  _  )(  _ \( ___)  / __)(  )(  )/ __)( )/ )/ __)
# )(__  )    (  /(__)\  )(_)(     )(   ) _ (  _)(_ \__ \  ( (__  )(_)(  )(_) ))__)   \__ \ )(__)(( (__  )  ( \__ \
#(____)(_/\/\_)(__)(__)(_____)   (__) (_) (_)(____)(___/   \___)(_____)(____/(____)  (___/(______)\___)(_)\_)(___/ 
