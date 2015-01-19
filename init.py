from smbus import SMBus
b = SMBus(1)

addr = 0x62


ret = block_process_call(addr, 0x81,[])
