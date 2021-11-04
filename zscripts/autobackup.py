import os
import sys

argn = len(sys.argv) - 1
argv = sys.argv

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
			mPrint('Hai creato un backup meno di un minuto fa!')
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

print('[autobackup] initialized.')
if __name__ == '__main__':
	print(argn)
	print(argv[1:])
	while True:
		pass
	