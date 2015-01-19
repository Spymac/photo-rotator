from smbus import SMBus
b = SMBus(1)

addr = 0x62


ret = b.block_process_call(addr, 0x81,[])
