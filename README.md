# Photo Rotator with TMC222 and LEDs

Python (SMBus) i2c communication with TMC222 stepper controller - used on Raspberry Pi. Good starting point for rotating motor.


#### Commands

```python
def getFullStatus1():           # Returns TMC222 getFullStatus1 command - Must be called to activate TMC222
def setMotorParam():            # Update TMC222 RAM (with configuration variables) - Must be called to drive motor
def resetPosition():            # Sets internal TMC222 position 0
def setPosition(newPosition):   # TMC222 
```

#### Used I2C functions
```bash
i2c_smbus_read_i2c_block_data()
i2c_smbus_write_i2c_block_data()
i2c_smbus_write_byte_data()
```

See also:
http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/plain/Documentation/i2c/smbus-protocol
