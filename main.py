import time
from Security import *

time.sleep(0.1) # Wait for USB to become ready

print("Hello, Pi Pico!")

s = GateSecurityController()
s.run()