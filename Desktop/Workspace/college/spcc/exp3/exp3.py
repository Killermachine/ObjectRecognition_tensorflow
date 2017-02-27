# exp 3 macro pass 1
file = open("sample_code.txt")
input = file.read()
lines=input.split('\n')
mntc = 1
mdtc = 1
mFlag = 0

class MntTable:
	index = 1
	row = []
	def __init__(self):
		self.index = 1
		self.row = []
	def addRow(self,name,mdtIndex):
		self.row.append((self.index,name,mdtIndex))
		self.index += 1

class MdtTable:
	index = 1
	row = []
	def __init__(self):
		self.index = 1
		self.row = []
	def addRow(self,card):
		self.row.append((self.index,card))
		self.index += 1

class AlaTable:
	index = 0
	row = []
	def __init__(self):
		self.index = 0
		self.row = []
	def addRow(self,argument):
		self.row.append((self.index,argument))
		self.index += 1

mntTable = MntTable()
mNameFlag = 0

mdtTable = MdtTable()

alaTable = AlaTable()

outputList = []
outputSourceCard = []
for line in lines:
	words = line.split(' ')
	
	if words[1] == 'MACRO':
		mFlag = 1
	elif words[1] == 'MEND':
		mFlag = -1

	if mFlag == 1 or mFlag == -1:
		if words[1] == "MACRO":
			outputList.append(words)
			mNameFlag = 1
			continue
		else:
			if mNameFlag == 1: 
				mntTable.addRow(words[1],mdtTable.index)
				mntc = mntTable.index
				print 'ala ',words[2].split('&')[1:]
				alaList = words[2].split('&')[1:]
				for i in alaList:
					alaTable.addRow(i.split(',')[0])
				mNameFlag = 0
		mdtTable.addRow(words)
		mdtc = mdtTable.index

		if mFlag == -1:
			mFlag = 0
		outputList.append(words)
	else:
		outputSourceCard.append(words)

# print mntTable
print "MNT TABLE AT ",mntTable
for i in mntTable.row:
	print i
print "mntc ",mntc
print "\n"

# print mdtTable
print "MDT TABLE AT ",mdtTable
for i in mdtTable.row:
	print i
print "mdtc ",mdtc
print "\n"

print "ala Table ",alaTable
for i in alaTable.row:
	print i
print "\n"

# print output table
print "Output"
for i in outputList:
	print i
print "\n"

# output source card
print "OutputSourceCard"
for i in outputSourceCard:
	print i
print "\n"