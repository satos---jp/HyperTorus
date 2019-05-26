from optparse import OptionParser
import sys

class Memory:
	def __init__(self):
		self.intpart = 0
		self.fracpart = 0
		self.keta = 0
		self.dir = 0
		self.data = {}
		
	def __str__(self):
		return "mp: %s memory: %s" % (self.pos_repr(),str(self.data))
	
	def pos_repr(self):
		a = bin(self.intpart)[2:].zfill(max(0,self.keta+1))[::-1]
		b = bin(self.fracpart)[2:].zfill(max(0,-self.keta))
		c = '-' if self.dir==1 else '+'
		if self.keta >= 0:
			a = a[:self.keta] + c + a[self.keta+1:]
		else:
			b = b[:-self.keta-1] + c + b[-self.keta:]
		return "%s.%s" % (a[::-1],b) 
	
	def pos(self):
		return self.pos_repr().replace('-','x').replace('+','x')
	
	def get(self):
		return self.data.get(self.pos(),0)
	
	def set(self,v):
		self.data[self.pos()] = v
	
	def turn(self,isLeft):
		if isLeft ^ (self.dir < 0):
			self.keta += 1
		else:
			self.keta -= 1
	
	def get_left_right(self):
		self.turn(True)
		left = self.get()
		self.turn(False)
		self.turn(False)
		right = self.get()
		self.turn(True)
		return (left,right)
		
	
	def operate(self,f):
		self.set(f(*self.get_left_right()))
	
	def inverse(self):
		self.dir = 1 - self.dir
		if self.keta >= 0:
			bit = 1<<self.keta
			self.intpart = (self.intpart & (~bit)) | (self.dir * bit)
		else:
			bit = 1<<(-self.keta+1)
			self.fracpart = (self.fracpart & (~bit)) | (self.dir * bit)

def run(program,read,write,dumpcond):
	bl = 1
	n = 2
	while n < len(program):
		n *= 2
		bl += 1
	program += '.' * (n-len(program))

	ip = 0
	ip_dir = 1
	def turn_ip_dir(c):
		nonlocal ip_dir
		sign = ip_dir // abs(ip_dir)
		ip_dir *= sign
		if (c == '<') ^ (sign < 0):
			ip_dir *= 2
			if ip_dir == n:
				ip_dir = 1
		else:
			if ip_dir == 1:
				ip_dir = n
			ip_dir //= 2
		ip_dir *= sign
	
	reg = 0
	isregset = False
	mem = Memory()
	while True:
		c = program[ip]
		if dumpcond(ip):
			sys.stderr.write("ip: (%s,%+d) inst: \'%c\'(%03d) %s\n" % (bin(ip)[2:].zfill(bl),ip_dir,c,ord(c),str(mem)))
		if c in '><?':
			if c=='?':
				if mem.get()==0:
					c = '<'
				else:
					c = '>'
			turn_ip_dir(c)
		elif c == '|':
			ip_dir *= -1
		elif c == '.':
			pass
		elif c == '@':
			break
		elif c in '0123456789abcdef':
			mem.set(int(c,16))
		elif c in '{}':
			mem.turn(c == '{')
		elif c == '$':
			mem.inverse()
		elif c in '+-*/%=()':
			if c == '+':
				f = lambda x,y: x+y
			elif c == '-':
				f = lambda x,y: x-y
			elif c == '*':
				f = lambda x,y: x*y
			elif c == '/':
				f = lambda x,y: x//y
			elif c == '%':
				f = lambda x,y: x%y
			elif c == '=':
				f = lambda x,y: 1 if x==y else 0
			elif c == '(':
				f = lambda x,y: 1 if x<y else 0
			elif c == ')':
				f = lambda x,y: 1 if x>y else 0
			mem.operate(f)
		elif c == '&':
			if not isregset:
				reg = mem.get()
			else:
				mem.set(reg)
			isregset = not isregset
		elif c == 'j':
			ip = ((mem.get()%n + n)%n) ^ abs(ip_dir)
		elif c == 'r':
			s = read()
			if len(s)==0:
				s = -1
			else:
				s = ord(s)
			mem.set(s)
		elif c == 'w':
			write(chr(mem.get() % 256))
		elif c == 'i':
			s = ""
			while True:
				c = read()
				if not c in "0123456789":
					break
				s += c
			mem.set(int(s,10))
		elif c == 'o':
			write("%d" % mem.get())
		else:
			sys.stderr.write('unknown character \'%s\'(%d)\n' % (c,ord(c)))
			exit(-1)
		
		ip ^= abs(ip_dir)



def main():
	parser = OptionParser()
	parser.add_option("-f", "--file", dest="file",help="path to sourcecode", metavar="FILE")
	parser.add_option("-n", "--dumpnum", dest="dumpnum",help="dump state for each NUM iterations", metavar="NUM")
	parser.add_option("-b", "--breakpoints", dest="breakpoints",help="breakpoint indicating string", metavar="BP")
	(options, args) = parser.parse_args()

	filename = options.file
	if filename is None:
		if len(args)==0:
			parser.usage = "usage: %prog [options] path/to/sourcecode"
			parser.print_help()
			exit(-1)
		filename = args[0]
		args = args[1:]
	
	dumpnum = options.dumpnum
	if dumpnum is not None:
		dumpnum = int(dumpnum)
	breakpoints = options.breakpoints
	stepcnt = 0
	def dumpcond(ip):
		nonlocal stepcnt,dumpnum,breakpoints
		stepcnt += 1
		if ((dumpnum is not None) and ((stepcnt-1) % dumpnum == 0)):
			return True 
		if (breakpoints is not None) and ip < len(breakpoints) and breakpoints[ip]=='#':
			return True 
		return False
	
	def write(s):
		sys.stdout.write(s)
		sys.stdout.flush()
	run(open(filename,'r').read().strip(),lambda: sys.stdin.read(1),write,dumpcond)
	

if __name__=='__main__':
	main()
