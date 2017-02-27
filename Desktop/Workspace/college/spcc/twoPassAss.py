class MOT:
	def __init__(self, filename):
		self.MOT = {}
		ins = [a.rstrip().split("\t") for a in open(filename)]
		self.strrep = self._strrep(ins)
		for a in ins:
			a[2] = int(a[2])
			self.MOT[a[0]] = tuple(a)

	def _strrep(self, ins):
		ans = ""
		for a in ins:
			for b in a:
				ans += b if not b == None else ''
				ans += '\t'
			ans += '\n'
		return ans

	def __str__(self):
		return self.strrep

	def find(self, key):
		return self.MOT.get(key, (None, None, None, None))


class POT:
	def __init__(self, filename):
		self.POT = {}
		ins = [a.rstrip().split("\t") for a in open(filename)]
		self.strrep = self._strrep(ins)
		for a in ins:
			self.POT[a[0]] = a[1]

	def _strrep(self, ins):
		ans = ""
		for a in ins:
			for b in a:
				ans += b if not b == None else ''
				ans += '\t'
			ans += '\n'
		return ans

	def __str__(self):
		return self.strrep

	def find(self, key):
		return self.POT.get(key, None)


class Assembler:
	def __init__(self, asm = "code2.asm", mot = "MOT.txt", pot = "POT.txt"):
		self.mot = MOT(mot)
		self.pot = POT(pot)
		self.st = []
		self.lt = []
		self.err = []
		self.txt_code = open(asm) # Code file
		self.code = None # Internal Rep
		self.code2 = []
		self.bt = []
		self.out = []
		self.lc = None # LC 


	def read_code(self):
		'''
		Prepare code in internal format (list of lists)
		'''
		self.code = []
		for line in self.txt_code:
			words = [w for w in line.rstrip().split("\t") if not w == ""]
			if len(words) == 2:
				words = [None, ] + words
			elif len(words) == 1:
				words = [None, ] + words + [None,]
			self.code.append(words)

	def get_code(self): 
		'''
		Get code in internal format (list of lists)
		'''
		if self.code:
			return self.code
		else:
			self.read_code()
			return self.code

	def print_code(self):
		if not self.code:
			self.read_code()
		for a in self.code:
			print(a)

	def pass_one(self):
		if not self.code: # Case if code was not already prepared
			self.read_code()

		self.lc = 0 # maybe

		for n, line in enumerate(self.code):
			old_lc = self.lc # to append in the output for next pass

			operands = None
			if line[2]:
				operands = [a.replace("'", '') for a in line[2].split(",") if not a == '']
			# POT instructions
			isPot = True
			if line[1] in ['DC', 'DS']:
				self._dcds(line[0], operands)
				self.code2.append(line + [n + 1, old_lc])
			elif line[1] == 'EQU':
				self._equ(line[0], operands)
			elif line[1] == 'START':
				self._start(line[0], operands)
			elif line[1] == 'LTORG':
				self._lit(True)
			elif line[1] == 'END':
				self._lit(False)
			elif self.pot.find(line[1]):
				self.code2.append(line + [n + 1, old_lc])
				continue # SKIP
			else:
				isPot = False
			# else in MOT
			if isPot: # i.e. work done
				continue

			if line[2]:
				for a in operands:
					if a[0] == '=':
						lit = [a[1:], None, 4, 'R']
						self.lt.append(lit)
				#print(line[1] + " " + "ins" + " " + str(n))
				ins, h, l, typ = self.mot.find(line[1])
				
				if ins:
					if line[0]: # if label
						sym = [line[0], self.lc, l, 'R']
						self.st.append(sym)
					self.lc += l
					self.code2.append(line + [n + 1,  old_lc])
					continue

			self.err.append([line[1], n + 1, 0 if not line[0] else len(line[0]) + 1])


	def pass_two(self):
		lt_top = 0;

		values = [None, None]
		last_symbol = None
		for i, line in enumerate(self.code2):
			# copy literals if any
			try:
				lit = self.lt[lt_top]
				while lit[1] < line[4]:
					# extract literal
					ans = [lit[1],]
					if lit[0][0] == 'F':
						ans.append("X'" + (9 - len(lit[0]))*'0' + lit[0][1:] + "'")
					else:
						ans.append(lit[0])
					self.out.append(ans)
					lt_top += 1
					lit = self.lt[lt_top]

			except IndexError:
				pass


			if line[2]:
				operands = [a.replace("'", '').replace(" ","") for a in line[2].split(",") if not a == '']

			# POT Instructions
			if line[1] == 'USING':
				if operands[0] == '*':
					values[0] = 0 if not last_symbol else self._get_val(last_symbol, self.st)
					values[1] = int(operands[1])
				else: # may have symbols 
					values[0] = self._get_val(operands[0], self.st)
					if not values[0]: values[0] = int(operands[0])
					values[1] = self._get_val(operands[1], self.st)
					if not values[1]: values[1] = int(operands[1])

				self.bt.append([values[1], values[0]]) 
			
			#	pass
			elif line[1] == 'DC':
				# remove F from first one 
				operands[0] = operands[0][1:]
				for oi, o in enumerate(operands):
					self.out.append( [oi * 4 + line[4], "X'" + (8 - len(o))*'0' + o + "'"])

			elif line[1] == 'DS': # Format 2000F
				if operands[0][-1] == 'F':
					for oi in range(0, int(operands[0][:-1])):
						self.out.append( [oi * 4 + line[4], "X'00000000'"])

			else: # MOT Entries
				ins, h, l, typ = self.mot.find(line[1])
				cout = [line[4], ins , h[:-1]]
				if cout[1] == "BNE":
					cout[1] = "BC" 
					cout += ["7,",]
				elif cout[1] == "BR":
					cout[1] = "BCR"
					cout += ["15,",]
				else:
					cout += ["",] # empty string to append to 

				if typ == 'RR':
					for o in operands:
						t = self._get_val(o, self.st)
						if not t: t = o
						cout[3] += str(t) + ","
					cout[3] = cout[3][:-1] # remove last comma
				else:
					if len(operands) == 1:
						cout[3] += self._offset(operands[0])
					else:
						t = self._get_val(operands[0], self.st)
						if not t: t = operands[0]
						cout[3] += str(t) + ","
						cout[3] += self._offset(operands[1])
				self.out.append(cout)

		# copy remaining literals if any
		try:
			lit = self.lt[lt_top]
			while True:
				# extract literal
				ans = [lit[1],]
				if lit[0][0] == 'F':
					ans.append("X'" + (9 - len(lit[0]))*'0' + lit[0][1:] + "'")
				else:
					ans.append(lit[0])
				self.out.append(ans)
				lt_top += 1
				lit = self.lt[lt_top]
		except IndexError:
			pass




	def _start(self, label, operands):
		if not operands:
			self.lc = 0
		else:
			self.lc = int(operands[0])
		sym = [label, self.lc, 1, 'R']
		self.st.append(sym)

	def _dcds(self, label, operands):
		if label:
			sym = [label, self.lc, 4, 'R']

		if operands[0][0] != 'F':
			l = int(operands[0][0:-1]) * 4; # case when operand is 2000F
		else: # starts with F and one or more literals
			l = len(operands)
		# add length to lc
		self.lc += l
		self.st.append(sym)

	def _equ(self, label, operands):
		if operands[0] == '*':
			sym = [label, self.lc, 1, 'R']
		else:
			sym = [label, self._eval(operands), 1, 'A']
		self.st.append(sym)

	def _eval(self, operands): 
		# Test function for current code
		return int(eval(operands[0]))

	def _lit(self, adjustLc):
		if adjustLc:
			l = self.lc + 8
			self.lc = l - (l % 8)
		for l in self.lt:
			if l[1] == None:
				l[1] = self.lc
				self.lc += 4 

	def _using(self, label, operands):
		pass

	def _get_val(self, symbol, table):
		for i in table:
			if i[0] == symbol:
				return i[1]
		return None

	def _offset(self, s):
		ind = 0
		index_reg = 0
		os = s # copy of original
		if s[0] == '=': # if literal
			value = self._get_val(s[1:], self.lt)
		else:
			bindex = s.find('(')
			if not bindex == -1:
				s = s[:bindex]
				index_reg = self._get_val(os[bindex+1:os.find(')')], self.st)
			value = self._get_val(s, self.st)

		offset = abs(value - self.bt[ind][1]) # last entry in bt

		for i, a in enumerate(self.bt):
			if i == 0:
				continue
			new_offset = abs(value - a[1])
			if new_offset < offset:
				offset = new_offset
				ind = i

		return str(offset) + '(' + str(index_reg) + ', ' + str(self.bt[ind][0]) + ')'


def rep(l):
	ans = ''
	for i in l:
		for j in i:
			ans += str(j) + '\t' 
		ans += '\n'
	return ans



assembler = Assembler()

ans = ""
test = []

# Display MOT/POT
print("MOT:-")
print(assembler.mot)
print("")
print("POT")
print(assembler.pot)
print("")

assembler.pass_one()

print("\n")
print("Code:-")
assembler.print_code()
print("\n")
print("ST:-")
print(rep(assembler.st))
print("LT:-")
print(rep(assembler.lt))

assembler.pass_two()

print("Next Pass Code:-")
print(rep(assembler.code2))
print("Output:-")
print(rep(assembler.out))
