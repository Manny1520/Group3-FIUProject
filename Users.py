import time
from machine import Timer, RTC
from Log import *

class User:
    def __init__(self, name, passcode, role):
        self.name = name
        self.passcode = passcode  
        self.role = role  # e.g., "admin", "user"

    def __str__(self): 
        return f"User(name={self.name}, role={self.role})"
    

