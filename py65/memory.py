from collections import defaultdict


class gpmem:
	def __setitem__(self, k, value):
		#print "setting"
		self.a[k] = value
		#if (k == 0x3016):
			#self.log = open("C:\\Users\\Natalie\\Documents\\logmcu.txt", 'a')
			#self.log.write("port b write")
			#self.log.close()
		if (k == 0x32):
			self.log = open("C:\\Users\\Natalie\\Documents\\logmcu.txt", 'a')
			self.log.write("im num write")
			#print "imnum"
			self.log.close()
		if (k == 0x3000):
			f = open("C:\\Users\\Natalie\\Documents\\p" + str(value) + ".bin", 'rb')
			print "paging " + str(value)
			t = f.read()
			for i in range(0x4000, 0xc000):
				self.a[i] = ord(t[i - 0x4000])
			#print "paging done" + str(value)	
		if ((k > 0x1000) & (k < 0x1200)):
			if (k != (self.plcd + 1)):
				self.log = open("C:\\Users\\Natalie\\Documents\\logmcu.txt", 'a')
				self.log.write("LCD write")
				self.log.close()
				print "end " + hex(self.plcd)
				print "OMG LCD " + hex(k)
			self.plcd = k
	def __getitem__(self, key):

		if isinstance( key, slice ) :
			return self.a[key.start:key.stop]
		#print "getting"
		#if (key == 0x3012):
			#self.log = open("C:\\Users\\Natalie\\Documents\\logmcu.txt", 'a')
			#self.log.write("port a read")
			#self.log.close()
		#if (key == 0x3016):
			#self.log = open("C:\\Users\\Natalie\\Documents\\logmcu.txt", 'a')
			#self.log.write("port b read")
			#self.log.close()
		return self.a[key]
	
	def __init__(self, size):
		print "init!"
		self.a = size * [0x00]
		self.plcd = 0	

class ObservableMemory:
    def __init__(self, subject=None, addrWidth=16):
        self.physMask = 0xffff
        if addrWidth > 16:
            # even with 32-bit address space, model only 256k memory
            self.physMask = 0x3ffff

        if subject is None:
            subject = gpmem(self.physMask + 1)
        self._subject = subject

        self._read_subscribers = defaultdict(list)
        self._write_subscribers = defaultdict(list)

    def __setitem__(self, address, value):
        address &= self.physMask
        callbacks = self._write_subscribers[address]

        for callback in callbacks:
            result = callback(address, value)
            if result is not None:
                value = result

        self._subject[address] = value

    def __getitem__(self, address):
	if isinstance( address, slice ) :
		return self._subject[address.start:address.stop]
        address &= self.physMask
        callbacks = self._read_subscribers[address]
        final_result = None

        for callback in callbacks:
            result = callback(address)
            if result is not None:
                final_result = result

        if final_result is None:
            return self._subject[address]
        else:
            return final_result

    def __getattr__(self, attribute):
        return getattr(self._subject, attribute)

    def subscribe_to_write(self, address_range, callback):
        for address in address_range:
            address &= self.physMask
            callbacks = self._write_subscribers.setdefault(address, [])
            if callback not in callbacks:
                callbacks.append(callback)

    def subscribe_to_read(self, address_range, callback):
        for address in address_range:
            address &= self.physMask
            callbacks = self._read_subscribers.setdefault(address, [])
            if callback not in callbacks:
                callbacks.append(callback)

    def write(self, start_address, bytes):
        start_address &= self.physMask
        self._subject[start_address:start_address + len(bytes)] = bytes
