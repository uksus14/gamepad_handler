import os
from json import dumps, loads
from inputs import devices, UnpluggedError
from time import time, sleep
# import mouse
from pynput.keyboard import Key, Controller
win_keyboard = Controller()
from pynput.mouse import Button, Controller
win_mouse = Controller()
class Mouse_filler:
    def __init__(self) -> None:
        pass
    def press(self, button):
        win_mouse.press(Button.__members__[button])
        # print(button)
    def release(self, button):
        win_mouse.release(Button.__members__[button])
    def click(self, button):
        self.press(button)
        self.release(button)
    def wheel(self, delta):
        win_mouse.scroll(0, delta)
    def move(self, x, y, absolute=True):
        if absolute:
            x1, y1 = win_mouse.position
            x -= x1
            y -= y1
        win_mouse.move(x, y)

mouse = Mouse_filler()
class Keyboard_filler:
    def __init__(self) -> None:
        pass
    def press(self, ks):
        for k in ks.replace("windows", "cmd").split("+"):
            if len(k) != 1:
                k = Key.__members__[k]
            win_keyboard.press(k)
            print(k)
    def release(self, ks):
        for k in ks.replace("windows", "cmd").split("+"):
            if len(k) != 1:
                k = Key.__members__[k]
            win_keyboard.release(k)
    def prsnrel(self, ks):
        self.press(ks)
        self.release(ks)
    def type(self, ks):
        win_keyboard.type(ks)
keyboard = Keyboard_filler()
last_input = [None, time()]
modes = ["general", "youtube"]
mode = 0
ready = False
STICK_MAX = 32766
wheel_delta, left, right, down, up, backspace, mouse_trans = 0, False, False, False, False, False, [0, 0]
TRIGGER_MAX = 255
wheel_alternate = 1700
arrows_alternate = 15000
mouse_alternate = 3000
mouse_move_per_frame = 3
backspace_alternate = 10000
arrow_buffer = 0.3
mode_buffer = 0.2
backspace_buffer = 0.3
parr_iter = 0
VEnvError = Exception("Enter virtual envirment")
try:
    pad = devices.gamepads[0]
    assert pad.parralel(), "Enter virtual envirment"
except AttributeError: raise VEnvError
except IndexError: raise UnpluggedError



def listen():
    global last_input
    while True:
        input = pad.read()[0]
        if input.code != "SYN_REPORT":
            last_input = [input, time()]
            return input.code, input.state
def new_listen():
    global last_input
    while last_input[0]:
        input = pad.read()[0]
        if input.code != last_input[0].code and input.code != "SYN_REPORT":
            last_input = [input, time()]
            return input.code, input.state
    input = pad.read()[0]
    last_input = [input, time()]
    return input.code, input.state

class MyGamePad:
    def __init__(self):
        self.actions = {"A": self.K_A, "B": self.K_B, "X": self.K_X, "Y": self.K_Y,
        "LB": self.L_BUMP, "RB": self.R_BUMP, "LT": self.L_TRIG, "RT": self.R_TRIG,
        "back": self.K_back, "start": self.K_start,
        "left horizontal": self.L_HSTICK, "left vertical": self.L_VSTICK, "LC": self.L_STICK,
        "right horizontal": self.R_HSTICK, "right vertical": self.R_VSTICK, "RC": self.R_STICK,
        "cross horizontal": self.HCROSS, "cross vertical": self.VCROSS}
        self.states = {label: 0 for label in self.actions}
        try:
            with open("./additional/button_codes.json", "r") as f:
                self.obj = loads(f.read())
            print("Автокалибровка прошла успешно!")
        except:
            print("Автокалибровка провалилась, начинаю калибровку")
            self.calibrate()
        # print(self.actions)
        # print(self.obj)
    def calibrate(self):
        self.obj = {}
        print("Калибровка началась")
        for label in self.actions:
            print(f"Input {label}")
            input = new_listen()
            self.obj[input[0]] = label
        print("Калибровка закончилась, спасибо")
        path = './additional'
        isExist = os.path.exists(path)
        if not isExist: os.makedirs(path)
        with open("./additional/button_codes.json", "w") as f:
            f.write(dumps(self.obj))
    def get_label(self, input):
        return self.obj[input]
    
    def oneortwo(self, state, one, two=None):
        if two is None: two = one
        oneon, oneoff, twoon, twooff = *one, *two
        if self.states["LT"]>=200:
            if state:
                twooff()
                oneon()
            else: oneoff()
        else:
            if state:
                oneoff()
                twoon()
            else: twooff()

    def doif(self, state, dolow, dohigh=None):
        if dohigh is None: dohigh = dolow
        if state:
            if self.states["LT"] >= 200:
                dohigh()
            else:
                dolow()

    def K_A(self, state):
        self.oneortwo(state, (lambda:mouse.press("left"), lambda:mouse.release("left")))

    def K_B(self, state):
        self.oneortwo(state, (lambda:mouse.press("middle"), lambda:mouse.release("middle")), (lambda:mouse.press("right"), lambda:mouse.release("right")))

    def K_X(self, state):
        if modes[mode] in ["general"]:
            self.oneortwo(state, (lambda:keyboard.press("alt"), lambda:keyboard.release("alt")), (lambda:keyboard.press("ctrl"), lambda:keyboard.release("ctrl")))
        if modes[mode] in ["youtube"] and state:
            keyboard.prsnrel("space")
        
    def K_Y(self, state):
        global backspace
        backspace = False
        if modes[mode] in ["youtube"] and state:
            keyboard.prsnrel("ctrl+w")
        if modes[mode] in ["general"]:
            if state == 0: keyboard.release("shift")
            if self.states["LT"]>=200:
                if state:
                    backspace = time()
                    keyboard.press("backspace")
            elif state: keyboard.press("shift")
    def L_BUMP(self, state):
        if modes[mode] in ["youtube"] and state:
            keyboard.prsnrel("tab")
        if modes[mode] in ["general"] and state:
            self.doif(state, lambda:keyboard.prsnrel("ctrl+x"), lambda:keyboard.prsnrel("ctrl+z"))

    def R_BUMP(self, state):
        if modes[mode] in ["youtube"] and state:
            keyboard.prsnrel("enter")
        if modes[mode] in ["general"] and state:
            self.doif(state, lambda:keyboard.prsnrel("ctrl+v"), lambda:keyboard.prsnrel("ctrl+y"))

    def L_TRIG(self, state):
        """stance key"""

    def R_TRIG(self, state):
        global wheel_alternate, mouse_alternate
        wheel_alternate, mouse_alternate = 1700, 3000
        def change_mode():
            global mode, ready
            if state >= 200 or not ready:
                ready = time()
            if state == 0:
                if time()-ready>mode_buffer:
                    mode = 0
                    print(f"now in {modes[mode]} mode")
                else:
                    mode += 1
                    mode %= len(modes)
                    print(f"now in {modes[mode]} mode")
        def speed_up():
            global wheel_alternate, mouse_alternate
            if state >= 200:
                wheel_alternate, mouse_alternate = 1700//5, 3000//5
        self.doif(1, change_mode, speed_up)

    def K_back(self, state):
        if modes[mode] in ["general"] and state:
            keyboard.prsnrel("tab")
        if modes[mode] in ["youtube"]:
            self.doif(state, lambda:keyboard.prsnrel("shift+,"), lambda:keyboard.prsnrel("alt+left"))

    def K_start(self, state):
        if modes[mode] in ["general"] and state:
            keyboard.prsnrel("enter")
        if modes[mode] in ["youtube"] and state:
            self.doif(state, lambda:keyboard.prsnrel("shift+."), lambda:keyboard.prsnrel("alt+right"))

    def L_HSTICK(self, state):
        global mouse_trans
        mouse_trans[0] = mouse_move_per_frame*state/STICK_MAX

    def L_VSTICK(self, state):
        global mouse_trans
        mouse_trans[1] = -mouse_move_per_frame*state/STICK_MAX

    def L_STICK(self, state):
        if modes[mode] in ["youtube"]:
            self.doif(state, lambda:keyboard.prsnrel("ctrl+t"), lambda:keyboard.prsnrel("ctrl+shift+t"))
        if modes[mode] in ["general"]:
            self.doif(state, lambda:keyboard.prsnrel("windows+e"))

    def R_HSTICK(self, state):
        if abs(state)<STICK_MAX:
            return None
        if self.states["LT"]>=200:
            keyboard.press("alt")
        else:
            keyboard.press("ctrl")
        if state<0:
            keyboard.press("shift")
        keyboard.press("tab")
        keyboard.release("ctrl+alt+shift+tab")

    def R_VSTICK(self, state):
        global wheel_delta
        wheel_delta = .05*state/STICK_MAX

    def R_STICK(self, state):
        if modes[mode] in ["youtube"] and state:
            keyboard.prsnrel("ctrl+r")
        if modes[mode] in ["general"] and state:
            keyboard.prsnrel("ctrl+t")
            keyboard.type("https://tsiauca.edupage.org/user/?")
            keyboard.prsnrel("enter")
            sleep(1)
            keyboard.press("shift")
            [keyboard.prsnrel("tab") for _ in range(7)]
            keyboard.release("shift")
            keyboard.prsnrel("enter")

    def HCROSS(self, state):
        global left, right
        if state == 0:
            left = False
            right = False
            return None
        if self.states["LT"]>=200:
            if state == 1:
                keyboard.prsnrel("ctrl+windows+right")
            else:
                keyboard.prsnrel("ctrl+windows+left")
        else:
            if state == -1:
                right = False
                left = time()
                keyboard.prsnrel("left")
            else:
                keyboard.prsnrel("right")
                right = time()
                left = False

    def VCROSS(self, state):
        global up, down
        if self.states["LT"]>=200:
            if state == -1:
                keyboard.prsnrel("windows+tab")
            elif state == 1:
                keyboard.prsnrel("windows+d")
        elif state == -1:
            down = False
            keyboard.prsnrel("up")
            up = time()
        elif state == 1:
            up = False
            down = time()
            keyboard.prsnrel("down")    
        else:
            up = False
            down = False


    def loop(self):
        global working
        working = False
        input = listen()
        working = True
        print("gamepad pc is up")
        while input:
            self.states[self.obj[input[0]]] = input[1]
            self.actions[self.obj[input[0]]](input[1])
            input = listen()
        return True
main = MyGamePad()
working = False
def parralel():
    global parr_iter
    parr_iter += 1
    parr_iter %= 1e9
    if parr_iter % backspace_alternate == 0:
        if backspace:
            if time()-backspace > backspace_buffer:
                keyboard.prsnrel("backspace")
    if parr_iter % mouse_alternate == 0:
        if any(mouse_trans):
            x, y = mouse_trans
            if main.states["LT"]>=200:
                x, y = x*3, y*3
            mouse.move(x, y, absolute=False)
    if parr_iter % arrows_alternate == 0:
        if left:
            if time()-left > arrow_buffer:
                keyboard.prsnrel("left")
        if right:
            if time()-right > arrow_buffer:
                keyboard.prsnrel("right")
        if up:
            if time()-up > arrow_buffer:
                keyboard.prsnrel("up")
        if down:
            if time()-down > arrow_buffer:
                keyboard.prsnrel("down")
    if parr_iter % wheel_alternate == 0:
        if main.states["LT"]>=200:
            mouse.wheel(3*wheel_delta)
        mouse.wheel(wheel_delta)
pad.parralel = parralel
if __name__ == '__main__':
    main.loop()