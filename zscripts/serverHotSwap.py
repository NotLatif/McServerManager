#TRIES TO FIX BUG at FIXME 0 (WIP)


server = {0: 'a', 1: 'b', 2: 'd', 3: 'e'}
tmpServerNames = ['a', 'b', 'd', 'e']
dirs =   ['a', 'b', 'd', 'e', 'g']
found = {}


#can only access server with server[x] (.name)
for x in range(len(tmpServerNames)): #server was removed
	if(tmpServerNames[x] not in dirs):
		found[x] = [tmpServerNames[x], 'rem', x]

y=len(dirs)	
for x in range(len(dirs)): #server was added
	if(dirs[x] not in tmpServerNames):
		found[x+y] = [dirs[x], 'add', x]

print(dirs)
print(found)
print()

x = 0
for find in found:
	if found[find][1] == 'rem':
		del server[found[find][2]]
		x-=1

	elif found[find][1] == 'add':
		server[found[find][2]] = found[x][0]
		x+=1
	x+=1

print(server)
print(found)
print(dirs)