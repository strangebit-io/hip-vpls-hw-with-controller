import ctypes
from ctypes import cdll
from array import array

lib = cdll.LoadLibrary('./aeslib.so')

class Aes(ctypes.Structure):
    pass

lib.freeme.argtypes = ctypes.POINTER(ctypes.c_ubyte),
lib.AES256.argtypes = ctypes.POINTER(ctypes.c_ubyte), 
lib.AES256.restype = ctypes.c_void_p #ctypes.POINTER(Aes)
lib.AES256EncryptBlock.argtypes = ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)
lib.AES256EncryptBlock.restype = ctypes.POINTER(ctypes.c_ubyte)
lib.AES256DecryptBlock.argtypes = ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)
lib.AES256DecryptBlock.restype = ctypes.POINTER(ctypes.c_ubyte)

class AES256HW(object):
    def __init__(self, key):
        print(key)
        v = array('I', key);
        addr, count = v.buffer_info();
        pkey = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte))
        #pkey = (ctypes.c_ubyte * len(key)).from_buffer(bytearray(key))
        self.obj = lib.AES256(pkey)

    def encrypt(self, data, iv):
        
        #s=time()
        v = array('I', data);
        #e=time()
        #print("Done with the initialization of array %f " % ((e-s)*1000))

        #s=time()
        addr, count = v.buffer_info();
        #e=time()
        #print("Done getting address of array %f " % ((e-s)*1000))
        #s=time()
        pdata = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte))
        #e=time()
        #print("Done with the casting in %f " % ((e-s)*1000))

        #s=time()
        v = array('I', iv);
        addr, count = v.buffer_info();
        piv = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte))
        #e=time()
        #print("Done with the casting (IV) in %f " % ((e-s)*1000))

        #pdata = (ctypes.c_ubyte * len(data))(*data)
        #piv = (ctypes.c_ubyte * len(iv))(*iv)

        addr = lib.AES256EncryptBlock(self.obj, len(data), pdata, piv)
        ciphertext = ctypes.string_at(addr, len(data))
        #ciphertext = ctypes.cast(addr, ctypes.c_char_p).value
        #ciphertext = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte * len(data))).value
        lib.freeme(addr);
        return ciphertext
        #e=time()
        #print("Done with the encryption in %f " % ((e-s)*1000))
    
    def decrypt(self, data, iv):
        #s=time()
        v = array('I', data);
        #e=time()
        #print("Done with the initialization of array %f " % ((e-s)*1000))

        #s=time()
        addr, count = v.buffer_info();
        #e=time()
        #print("Done getting address of array %f " % ((e-s)*1000))
        #s=time()
        pdata = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte))
        #e=time()
        #print("Done with the casting in %f " % ((e-s)*1000))

        #s=time()
        v = array('I', iv);
        addr, count = v.buffer_info();
        piv = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte))
        #e=time()
        #print("Done with the casting (IV) in %f " % ((e-s)*1000))

        #pdata = (ctypes.c_ubyte * len(data))(*data)
        #piv = (ctypes.c_ubyte * len(iv))(*iv)
        #s=time()
        addr = lib.AES256DecryptBlock(self.obj, len(data), pdata, piv)
        #plaintext = ctypes.cast(addr, ctypes.c_char_p).value
        plaintext = ctypes.string_at(addr, len(data))
        #plaintext = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte * len(data)))
        lib.freeme(addr);
        return plaintext
