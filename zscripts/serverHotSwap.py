#TRIES TO FIX BUG at FIXME 0 (WIP)
server = {0: 'a', 1: 'd', 2: 'e', 3: 'h'}
tmpServerNames = [server[x] for x in server] #copy of above

dirs =   ['a', 'b', 'd', 'e', 'g']
found = {}


# can only access server with server[x] (.name)

for x in range(len(tmpServerNames)): #server was removed
	if(tmpServerNames[x] not in dirs):
		found[len(found)] = [tmpServerNames[x], 'rem', x]

for x in range(len(dirs)): #server was added
	if(dirs[x] not in tmpServerNames):
		found[len(found)] = [dirs[x], 'add', x]

print(server)
print(dirs)
print(found)
print()

x = 0
for find in found:
	if found[find][1] == 'rem':
		server[found[find][2]] = ''

	elif found[find][1] == 'add':
		server[found[find][2]] = found[x][0]

	x+=1

print(f'new -> {server}')
print(dirs)
print()