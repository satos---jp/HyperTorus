from optparse import OptionParser
import sys

class Memory:
	def __init__(self):
		self.stack = []
		
	def __str__(self):
		return "stack: %s" % (self.stack)
	
	
	def push(self,x):
		self.stack.append(x)
	def pop(self):
		return self.stack.pop()
	def push_bottom(self,x):
		self.stack = [x] + self.stack
	def pop_bottom(self):
		res = self.stack[0]
		self.stack = self.stack[1:]
		return res

def run(program,read,write,dumpcond):
	bl = 1
	n = 2
	while n < len(program):
		n *= 2
		bl += 1
	program += '.' * (n-len(program))
	program = list(program)

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
	
	def ip_mod(p):
		return ((p%n + n)%n)
	
	reg = 0
	isregset = False
	mem = Memory()
	while True:
		c = program[ip]
		if dumpcond(ip):
			sys.stderr.write("ip: (%s,%+d) inst: \'%c\'(%03d) %s\n" % (bin(ip)[2:].zfill(bl),ip_dir,c,ord(c),str(mem)))
		
		# IP operation
		if c in '><?':
			if c=='?':
				if mem.pop()==0:
					c = '<'
				else:
					c = '>'
			turn_ip_dir(c)
		elif c == '|':
			ip_dir *= -1
		elif c == 'j':
			ip = ip_mod(mem.pop()) ^ abs(ip_dir)
		elif c == '.':
			pass
		elif c == 'q':
			break
		# stack state operation
		elif c == '$':
			p = mem.pop()
			q = mem.pop()
			mem.push(p)
			mem.push(q)
		elif c == '@':
			p = mem.pop()
			q = mem.pop()
			r = mem.pop()
			mem.push(p)
			mem.push(r)
			mem.push(q)
		elif c == ':':
			p = mem.pop()
			mem.push(p)
			mem.push(p)
		elif c == '@':
			mem.pop()
		elif c == '}':
			a = mem.pop()
			mem.push_bottom(a)
		elif c == '{':
			a = mem.pop_bottom()
			mem.push(a)
		#reflection
		elif c == 'g':
			p = mem.pop()
			mem.push(program[ip_mod(p)])
		elif c == 'p':
			p = mem.pop()
			v = mem.pop()
			program[ip_mod(p)] = chr(((v%256)+256)%256)
		# set value
		elif c in '0123456789abcdef':
			mem.push(int(c,16))
		elif c == '&':
			if not isregset:
				reg = mem.pop()
			else:
				mem.push(reg)
			isregset = not isregset
		# binary operation
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
			r = mem.pop()
			l = mem.pop()
			mem.push(f(l,r))

		# IO operation
		elif c == 'r':
			s = read()
			if len(s)==0:
				s = -1
			else:
				s = ord(s)
			mem.push(s)
		elif c == 'w':
			write(chr(mem.pop() % 256))
		elif c == 'i':
			s = ""
			while True:
				c = read()
				if not c in "0123456789":
					break
				s += c
			mem.push(int(s,10))
		elif c == 'o':
			write("%d" % mem.pop())
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
