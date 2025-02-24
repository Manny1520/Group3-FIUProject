"""
A basic template file for using the Model class in PicoLibrary
This will allow you to implement simple Statemodels with some basic
event-based transitions.
"""

# Import whatever Library classes you need - StateModel is obviously needed
# Counters imported for Timer functionality, Button imported for button events
import time
import random
from Log import *
from StateModel import *
from Counters import *
from Button import *
from Displays import *
from Motors import *
from Keypad import *
from Users import *

"""
This is the template for a Controller - you should rename this class to something
that is supported by your class diagram. This should associate with your other
classes, and any PicoLibrary classes. If you are using Buttons, you will implement
buttonPressed and buttonReleased.

To implement the state model, you will need to implement __init__ and 4 other methods
to support model start, stop, entry actions, exit actions, and state actions.

The following methods must be implemented:
__init__: create instances of your View and Business model classes, create an instance
of the StateModel with the necessary number of states and add the transitions, buttons
and timers that the StateModel needs

stateEntered(self, state, event) - Entry actions
stateLeft(self, state, event) - Exit actions
stateDo(self, state) - do Activities

# A couple other methods are available - but they can be left alone for most purposes

run(self) - runs the State Model - this will start at State 0 and drive the state model
stop(self) - stops the State Model - will stop processing events and stop the timers

This template currently implements a very simple state model that uses a button to
transition from state 0 to state 1 then a 5 second timer to go back to state 0.
"""

class GateSecurityController:

    def __init__(self):
        
        # Instantiate whatever classes from your own model that you need to control
        # Handlers can now be set to None - we will add them to the model and it will
        # do the handling
        self._users = [
            User("Matt", "1234", "admin"),  
            User("Alex", "4321", "user1"),
            User("Shalini","1111","user2"),
            User("Manny","2222","user3"),
            User("Zach","3333","user4")] 
        self.current_user = None  
        self._entry_code = []

        self._display = LCDDisplay(sda=0, scl=1)
        self._servo = Servo(16, "Gate")
        self._keypad = Keypad(row_pins=[2, 3, 4, 5], col_pins=[6, 7, 8, 9])
        #self._passcode = "1111"
        self._entry_code = []

        # Instantiate a Model. Needs to have the number of states, self as the handler
        # You can also say debug=True to see some of the transitions on the screen
        # Here is a sample for a model with 4 states
        self._model = StateModel(7, self, debug=True)
        
        # Instantiate any Buttons that you want to process events from and add
        # them to the model
        #self._button = Button(20, "button1", handler=None)        
        #self._model.addButton(self._button)
        
        # add other buttons if needed. Note that button names must be distinct
        # for all buttons. Events will come back with [buttonname]_press and
        # [buttonname]_release
        
        # Add any timer you have. Multiple timers may be added but they must all
        # have distinct names. Events come back as [timername}_timeout
        #self._timer = SoftwareTimer(name="timer1", handler=None)
        #self._model.addTimer(self._timer)

        # Add any custom events as appropriate for your state model. e.g.
        # self._model.addCustomEvent("collision_detected")
        self._model.addCustomEvent("wait_for_input")
        self._model.addCustomEvent("enter_passcode")
        self._model.addCustomEvent("verify_passcode")
        self._model.addCustomEvent("correct_passcode")
        self._model.addCustomEvent("access_granted")
        self._model.addCustomEvent("close_gate")
        self._model.addCustomEvent("incorrect_passcode")
        
        # Now add all the transitions from your state model. Any custom events
        # must be defined above first. You can have a state transition to another
        # state based on multiple events - which is why the eventlist is an array
        # Syntax: self._model.addTransition( SOURCESTATE, [eventlist], DESTSTATE)
        
        # some examples:
        self._model.addTransition(0, ["enter_passcode"], 1)
        self._model.addTransition(1, ["verify_passcode"], 2)
        self._model.addTransition(2, ["correct_passcode"], 3)
        self._model.addTransition(2, ["incorrect_passcode"], 6)
        self._model.addTransition(3, ["access_granted"], 4)
        self._model.addTransition(4, ["close_gate"], 5)
        self._model.addTransition(5, ["no_event"], 0) #<<-- should this be 5,1
        self._model.addTransition(6, ["enter_passcode"], 0) #<<-- should this be 6,1
        
        # etc.
    
    def stateEntered(self, state, event):
        """
        stateEntered - is the handler for performing entry actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        """
        
        # If statements to do whatever entry/actions you need for
        # for states that have entry actions
        Log.d(f'State {state} entered on event {event}')
        if state == 0:
            # entry actions for state 0
            self._display.clear()
            self._display.showText("Enter code")
            self.close_gate()
            self._model.processEvent("enter_passcode")

        elif state == 1:
            # entry actions for state 1
            self._entry_code = []

        elif state == 2:
            self.verify_passcode()

        elif state == 3:
            self.open_gate()
        
        elif state == 4:
            self.wait_to_close_gate()

        elif state == 5:
            self.close_gate()

    def enter_passcode(self):
        key = self._keypad.scanKey()
        #print(f"    key = {key}")
        if key is not None and key.isdigit() and len(self._entry_code) < 4:
            self._entry_code.append(key)
            self._display.clear()
            self._display.showText("".join(self._entry_code)) # show entered digits
            
            # If full passcode is entered, transition immediately
            if len(self._entry_code) == 4:
                Log.d("Passcode entered completely, transitioning to verify...")
                self._model.processEvent("verify_passcode")
    
    def close_gate(self):
        self._servo.setAngle(180)
        #self._model.processEvent("enter_passcode")

    def wait_to_close_gate(self):
        self._display.clear()
        i = 5
        while i > 0:
            self._display.showText(f"Closing in {i}")
            time.sleep(1)
            i -= 1

        self._model.processEvent("close_gate")

    def open_gate(self):
        self._servo.setAngle(90)
        self._model.processEvent("access_granted")

    def verify_passcode(self):
        entry = "".join(self._entry_code)
        self._entry_code = []
        self.current_user = None # Reset the current user for the next entry
        for user in self._users:
            if entry == user.passcode:
                self.current_user = user
                break  
        if self.current_user:  # Successful authentication
            Log.i(f"Access Granted for {self.current_user}")
            self._display.clear()
            self._display.showText("Access Granted!")
            self._display.showText(f"Welcome,{self.current_user.name}!",1)
            time.sleep(2)
            self._model.processEvent("correct_passcode")
        else:
            Log.i("Access Denied!")
            self._display.showText("Access Denied!")
            self._model.processEvent("incorrect_passcode")
            time.sleep(2)
            self._model.processEvent("enter_passcode")

    def stateLeft(self, state, event):
        """
        stateLeft - is the handler for performing exit/actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        
        This is just like stateEntered, perform only exit/actions here
        """

        Log.d(f'State {state} exited on event {event}')
        if state == 0:
            # exit actions for state 0
            pass
        # etc.
    
    def stateEvent(self, state, event)->bool:
        """
        stateEvent - handler for performing actions for a specific event
        without leaving the current state. 
        Note that transitions take precedence over state events, so if you
        have a transition as well as an in-state action for the same event,
        the in-state action will never be called.

        This handler must return True if the event was processed, otherwise
        must return False.
        """
        
        # Recommend using the debug statement below ONLY if necessary - may
        # generate a lot of useless debug information.
        # Log.d(f'State {state} received event {event}')
        
        # Handle internal events here - if you need to do something
        if state == 0 and event == 'button1_press':
            # do something for button1 press in state 0 wihout transitioning
            self._timer.cancel()
            return True
        
        # Note the return False if notne of the conditions are met
        return False

    def stateDo(self, state):
        """
        stateDo - the method that handles the do/actions for each state
        """
        
        # Now if you want to do different things for each state that has do actions
        if state == 0:
            # State 0 do/actions
            pass
        elif state == 1:
            # State1 do/actions
            # You can check your sensors here and process events manually if custom events
            # are needed (these must be previously added using addCustomEvent()
            # For example, if you want to go from state 1 to state 2 when the motion sensor
            # is tripped you can do something like this
            # In __init__ - you should have done self._model.addCustomEvent("motion")
            # Here, you check the conditions that should check for this condition
            # Then ask the model to handle the event
            # if self.motionsensor.tripped():
            #    self._model.processEvent("motion")
            #self._model.processEvent("enter_passcode")
            self.enter_passcode()
        
    def run(self):
        """
        Create a run() method - you can call it anything you want really, but
        this is what you will need to call from main.py or someplace to start
        the state model.
        """
        
        # The run method should simply do any initializations (if needed)
        # and then call the model's run method.
        # You can send a delay as a parameter if you want something other
        # than the default 0.1s. e.g.,  self._model.run(0.25)
        self._model.run()

    def stop(self):
        # The stop method should simply do any cleanup as needed
        # and then call the model's stop method.
        # This removes the button's handlers but will need to see
        # if the IRQ handlers should also be removed
        self._model.stop()
        

# Test your model. Note that this only runs the template class above
# If you are using a separate main.py or other control script,
# you will run your model from there.
if __name__ == '__main__':
    p = GateSecurityController()
    try:
        p.run()
    except KeyboardInterrupt:
        p.stop()    
