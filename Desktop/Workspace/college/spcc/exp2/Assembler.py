# Code for two pass assembler

from collections import OrderedDict
import pdb
file = open("sample_code2.txt")
input = file.read()
lines=input.split('\n')
LC=0
# Look up Tables

# psudoOpCode , Address of the subroutine
POT={
	"START"	:["P1START"],
	"USING"	:["P1USING"],
	"EQU"	:["P1EQU"],
	"DROP"	:["P1DROP"],
	"END"	:["P1END"],
	"DC"	:["P1DC"],
	"DS"	:["P1DS"],
	"LTORG"	:["P1LTORG"]
	}

# MneumonicOpCode , Binary opcode , instruction length, inst format
MOT={
	"L"		:[0xA9,0b10,0b001],
	"A"		:[0x95,0b10,0b001],
	"AH"	:[0x3B,0b10,0b001],
	"AL"	:[0x39,0b10,0b001],
	"ALR"	:[0x1E,0b01,0b000],
	"ST"	:[0x80,0b10,0b001],
	"LA"	:[0x18,0b10,0b001],
	"SR"	:[0x88,0b01,0b000],
	"AR"	:[0x1F,0b01,0b000],
	"C"		:[0x92,0b10,0b001],
	"LR"	:[0x11,0b01,0b000],
	"BNE"	:[0xEE,0b10,0b011],
	"BR"	:[0xD1,0b11,0b100],
	"MVC"	:[0xD2,0b11,0b100]}

# Symbol , value , length , relocation
ST=OrderedDict({"":["","",""]})

# Literal, value , length , relocation
LT=OrderedDict({"":["","",""]})

LENGTH=0

print "\n********** PASS-1 **********"
for line in lines:
	words=line.split(' ')
# Search for mnemonic in POT
	if words[1] in POT:
		if words[1]=="START":
			LC=int(words[2])
			if len(words[0])>0:
				ST.update({words[0]:[LC,1,'R']})
		elif words[1]=="DC":
			count=words[2].count('F')+words[2].count(',')
			LENGTH=count*4
			if len(words[0])>0:
				ST.update({words[0]:[LC,4,'R']})
				LC+=LENGTH
			else:
				print "Syntax error"
		elif words[1]=="DS":
			LENGTH=4*int(words[2][:-1])
			if len(words[0])>0:
				ST.update({words[0]:[LC,4,'R']})
				LC+=LENGTH
			else:
				print "Syntax error"
		elif words[1]=="EQU":
			if len(words[2])!=0 and words[2]!='*':
				print words[2]
				ST.update({words[0]:[int(words[2]),1,'A']})
			elif words[2]=='*':
				ST.update({words[0]:[LC,4,'R']})
			else:
				print "Syntax error"
		elif words[1]=="END" or words[1]=="LTORG":
# Assigning location(value) to literals in literal table
			if (LC%8)==0:
				for key in LT.keys():
					if len(key)!=0 and LT[key][0]=='':
						LT[key]=[LC,4,'R']
						LC+=4
			else:
				LC=LC-(LC%8)+8
				for key in LT.keys():
					if len(key)!=0 and LT[key][0]=='':
						LT[key]=[LC,4,'R']
						LC+=4
		else:
			pass
# Search for mnemonic in MOT
	elif words[1] in MOT:
		TEMP=words[1]
		LENGTH=MOT[TEMP][1]*2
		if words[2].count('=')!=0:
			TEMP=words[2].index('=')
			LITERAL=words[2][TEMP+1:]
			LT.update({LITERAL:['','','']})
		if len(words[0])>0:
			ST.update({words[0]:[LC,4,'R']})
		LC+=LENGTH
	else:
		print "Syntax error: Invalid mnemonic",words[1]
# Printing all the tables after pass-1
print "\nPrinting PSEUDO-OP TABLE\n"
print "_____________________________________________________________________"
print "{:<20} {:<20}".format('Pseudo-op','Address of subroutine')
print "_____________________________________________________________________"
for k, v in POT.iteritems():
        Address = v
        print "{:<20} {:<20}".format(k, Address)

print "\nPrinting MACHINE-OP TABLE\n"
print "_____________________________________________________________________________________________________________"
print "{:<20} {:<25} {:<25} {:<20}".format('Machine-op','Binary op-code','Instruction length','Instruction format')
print "_____________________________________________________________________________________________________________"
for k, v in MOT.iteritems():
        BinaryCode,Length,Format = v
        print "{:20} {:<25} {:<25} {:<20}".format(k,hex(BinaryCode)[2:],bin(Length)[2:],bin(Format)[2:])

print "\nPrinting SYMBOL TABLE\n"
print "_______________________________________________________________________________________"
print "{:<8} {:<15} {:<10} {:<10}".format('Symbol','Value','Length','Relocation')
print "_______________________________________________________________________________________"
for k, v in ST.iteritems():
        Value, Length, Relocation = v
        print "{:<8} {:<15} {:<10} {:10}".format(k, Value, Length, Relocation)

print "\nPrinting LITERAL TABLE\n"
print "_______________________________________________________________________________________"
print "{:<15} {:<15} {:<15} {:<15}".format('Literal','Value','Length','Relocation')
print "_______________________________________________________________________________________"
for k, v in LT.iteritems():
        Value, Length, Relocation = v
        print "{:<15} {:<15} {:<15} {:15}".format(k, Value, Length, Relocation)

# Printing final value of LC after pass-1
print "\nFinal value of LC after pass-1: ",LC

print "\n********** PASS-2 **********\n"

LC = 0
# Lookup tables for pass-2

# Initialising dictionary for machine code generated after pass-2
MCODE = OrderedDict({"":["","",""]})

# Initialising base table
BT={}
for i in range(0,16):
	BT.update({i:["N",' ']})
	
for line in lines:
	words=line.split(' ')
	if words[1] in POT:
		if words[1] == "START" or words[1] == "EQU":
			pass
		elif words[1] == "USING":
			src = words[2].split(",")[0] 
			dst = words[2].split(",")[1]
			if not isinstance(dst,int):  
				if dst in ST:
					dst = ST[dst][0]
			if src == "*":
				for key in BT.keys():
					# If dst is a mnemonic
					if key == dst:
						BT[dst] = "Y",LC
					# If dst is a value	
					else:
						BT[dst] = "Y",LC
			else:
				for k,v in ST.iteritems():
					if k == src:
						src_val = v[0]
				for key in BT.keys():
					if key == dst:
						BT[dst] = "Y",src_val
		elif words[1] == "DC":
			count=words[2].count('F')+words[2].count(',')
			LENGTH=count*4
			MCODE.update({LC:[words[2][2:-1],"",""]})
			LC = LC + LENGTH
		elif words[1] == "DS":
			MCODE.update({LC:["","",""]})
			LENGTH=4*int(words[2][:-1])
			LC+=LENGTH
		elif words[1] == "DROP":
			if words[2] in BT:	
				BT[words[2]] = "N",None
		elif words[1] == "END":
			pass
		elif words[1] == "LTORG":
			if (LC%8)!=0:
				LC=LC-(LC%8)+8
			for k in LT.keys():
				if "(" in k:
					t_o2 = k.split('(')[1]
					t_o2 = t_o2.split(')')[0]
					MCODE.update({LC:[ST[t_o2][0],"",""]})
					LC+=4                  
				else:
					if len(k.split("'")) >1:
						t_o2 = k.split("'")[1]
						MCODE.update({LC:[t_o2,"",""]})
						LC+=4
	elif words[1] in MOT:
		if MOT[words[1]][2] == 0:
			operands=words[2].split(',')
			if operands[0] in ST:
				op1 = ST[operands[0]][0]
			else:
				op1 = operands[0]
			op2 = ST[operands[1]][0]
			MCODE.update({LC:[words[1],op1,op2]})
			LENGTH = MOT[words[1]][1]*2
			LC = LC + LENGTH
		if MOT[words[1]][2] == 1:
			operands=words[2].split(',')
			if operands[0] in ST:
				op1 = ST[operands[0]][0]
			else:
				op1 = operands[0]
			if '=' in operands[1]: 
				op2 = operands[1][1:]
			else:
				op2=operands[1]
			if op2 in ST.keys():
				o2=ST[op2][0]
			elif op2 in LT.keys():
				o2=LT[op2][0]
			else:
				t_o2 = op2.split('(')[1]
				t_o2 = t_o2.split(')')[0]
				t_label = op2.split('(')[0]
				o2 = ST[t_label][0]
			if o2!='':
				min_ = 9999
				for k in BT.keys():
					if BT[k][0] == "Y":
						if o2 - BT[k][1] <= min_ and o2-BT[k][1]>=0:
							min_ = o2 - BT[k][1]
							base = k
						tp=[0,int(base)]
						s=str(min_)+str(tp)
			MCODE.update({LC:[words[1],op1,s]})
			LENGTH = MOT[words[1]][1]*2
			LC = LC + LENGTH
		if MOT[words[1]][2] == 3:
			min_ = 9999
			o2 = ST[words[2]][0]
			for k in BT.keys():
				if BT[k][0] == "Y":
					if o2 - BT[k][1] <= min_ and o2-BT[k][1]>=0:
						min_ = o2 - BT[k][1]
						base = k
					tp=[0,int(base)]
					s=str(min_)+str(tp)
			MCODE.update({LC:["BC",7,s]})
			LENGTH = MOT[words[1]][1]*2
			LC = LC + LENGTH
		if MOT[words[1]][2] == 4:
			MCODE.update({LC:["BCR",15,words[2]]})
			LENGTH = MOT[words[1]][1]*2
			LC = LC + LENGTH
print "_____________________________________________________________________"
print "\nPrinting BASE TABLE\n"
print "_____________________________________________________________________"
for k,v in BT.iteritems():
	print str(k)+"\t"+str(v[0])+"\t"+str(v[1])
print "_____________________________________________________________________"
print "\nPrinting GENERATED MACHINE CODE:\n"
print "_____________________________________________________________________"
for k,v in MCODE.iteritems():
	v1,v2,v3 = v
	print str(k)+"\t"+str(v1)+"\t"+str(v2)+"\t"+str(v3)