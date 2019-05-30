from interpreter import run


def check(code,inbyte,outbyte):
	inp = 0
	def infunc():
		nonlocal inp
		if inp < len(inbyte):
			inp += 1
			return bytes([inbyte[inp-1]])
		else:
			return b''
	
	res = b''
	def outfunc(s):
		nonlocal res
		res += s
	
	run(code,infunc,outfunc,lambda _: True)
	if res == outbyte:
		return True
	else:
		print('check failure')
		print('code:',code)
		print('expect:',outbyte)
		print('result:',res)
		assert False


def toseq(prog):
	n = 2 ** len(prog)
	res = [ord('`') for _ in range(n)]
	idxs = [(2 ** i) ^ 1 for i in range(len(prog))]
	res[1] = ord('<')
	for i,c in zip(idxs,prog):
		res[i] = c
	return bytes(res)

#ip operations
check(b'q',b'',b'')
check(b'q`',b'',b'')
check(b'q``',b'',b'')
check(b'.q``',b'',b'')
check(b'.<`q````',b'',b'')
check(b'.>```q``',b'',b'')
check(b'|q``',b'',b'')
check(b'|<```q``',b'',b'')
check(b'|>`q````',b'',b'')
check(b'0?`q````',b'',b'')
check(b'1?```q``',b'',b'')
check(b'6j````q`',b'',b'')
check(b'6j````.q',b'',b'')
check(b'6j``q`<`',b'',b'')

#IO operations
check(b'a<`w`q``',b'',b'\n')
check(b'3<`7`-```w```````q',b'',bytes([256-4]))
check(toseq(b'37-wq'),b'',bytes([256-4]))
check(toseq(b'ab*ef*+wq'),b'',bytes([64]))
check(toseq(b'eoq'),b'',b'14')
check(toseq(b'37-oq'),b'',b'-4')
check(toseq(b'ab*ef*+oq'),b'',b'320')
check(toseq(b'roq'),b'\x03',b'3')
check(toseq(b'rororoq'),b'\x03',b'3-1-1')
check(toseq(b'ioq'),b'12 ',b'12')
check(toseq(b'ioroq'),b'12p\x03',b'123')
# check(toseq(b'ioroq'),b'-12p\x03',b'-123')

#set value
for i in range(16):
	check(toseq(b'%xwq' %i),b'',bytes([i]))
check(toseq(b'5&4&oq'),b'',b'5')

# stack operation
check(toseq(b'1234$ooooq'),b'',b'3421')
check(toseq(b'1234@ooooq'),b'',b'3241')
check(toseq(b'1234{ooooq'),b'',b'1432')
check(toseq(b'1234}ooooq'),b'',b'3214')
check(toseq(b'1234:oooooq'),b'',b'44321')
check(toseq(b'1234~oooq'),b'',b'321')

#reflection
check(b'6<`g`wh``q',b'',b'h')
check(b'6<`g`w\xef``q',b'',b'\xef')
check(b'e<`f`*```g```````wh``````````````q',b'',b'h')
check(b'4<`7`-```g```````w```````````````q```````````````````````````h``',b'',b'h')
check(b'7<.8`*``w2>q``.``p````````.``````a````````.``````````````````````j',b'',b'\x08')

# binary operation
check(toseq(b'e5+oq'),b'',b'19')
check(toseq(b'e5-oq'),b'',b'9')
check(toseq(b'e5*oq'),b'',b'70')
check(toseq(b'e5/oq'),b'',b'2')
check(toseq(b'e5%oq'),b'',b'4')
check(toseq(b'23=oq'),b'',b'0')
check(toseq(b'33=oq'),b'',b'1')
check(toseq(b'e5(oq'),b'',b'0')
check(toseq(b'55(oq'),b'',b'0')
check(toseq(b'5e(oq'),b'',b'1')
check(toseq(b'e5)oq'),b'',b'1')
check(toseq(b'55)oq'),b'',b'0')
check(toseq(b'5e)oq'),b'',b'0')


# cat.hyp
check(open('cat.hyp','rb').read(),b'Hello',b'Hello')

# box.hyp
check(open('box.hyp','rb').read(),b'12\n34\n',(b'*' * 34) + b'\n' + (b'*' + b' ' * 32 + b'*\n') * 10 + (b'*' * 34) + b'\n')




