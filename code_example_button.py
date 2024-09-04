#how to read tap, double tap, long tap

import board
import pwmio
import displayio
import time
from digitalio import DigitalInOut, Direction, Pull
import _music
import time


from i2cdisplaybus import I2CDisplayBus
    
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

def setup():
    displayio.release_displays()
    W = 64
    H = 32
    i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
    display_bus = I2CDisplayBus(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=W, height=H)
    # Make the display context
    splash = displayio.Group()
    display.root_group = splash

    piezo = pwmio.PWMOut(board.A0, frequency=440, duty_cycle=0,variable_frequency=True)
    
    switches = []
    for button in [board.A1, board.A2, board.A3]:
        switch = DigitalInOut(button)
        # switch = DigitalInOut(board.D5)  # For Feather M0 Express, Feather M4 Express
        # switch = DigitalInOut(board.D7)  # For Circuit Playground Express
        switch.direction = Direction.INPUT
        switch.pull = Pull.UP
        switches.append(switch)
    return piezo, W, H, display, splash, switches




def make_text(splash, _txt, offset = (1,1)):
    # Draw a label
    text = "Hello World!"
    text_area = label.Label(terminalio.FONT, text=_txt, color=0xFFFF00, x=offset[0], y=offset[1])
    splash.append(text_area)

def beep(piezo, switches):
    eff = [(x, .25) for x in (262, 294, 330, 349, 392, 440, 494, 523)]
    while True:
        _music.play_frequencies(piezo, eff,interrupt_buttons = switches)
        if any([x.value for x in switches]):
            return
    
    _break = False
    while True:
        for f in eff:
            _break = any([x.value for x in switches])
            if _break:
                piezo.duty_cycle = 0
                return
            piezo.frequency = f
            piezo.duty_cycle = 65535 // 2  # On 50%
            time.sleep(0.25)  # On for 1/4 second
            piezo.duty_cycle = 0  # Off
            time.sleep(0.05)  # Pause between notes
    time.sleep(0.5)
    piezo.duty_cycle = 0

def bad_sleep(_secs):
    start = time.monotonic()
    while time.monotonic() - start < _secs:
        if _music.interrupt_check(switches):
            return
        time.sleep(1)    
    return

def chirp(piezo):
    _music.play_frequencies(piezo, [(2500, .15),(1500, .15),(4000, .1) ],interrupt_buttons = None)

def chirp_start(piezo):
    _music.play_frequencies(piezo, [(2500, .15),(1500, .15),(1500, .1) ],interrupt_buttons = None)


def pomodoro(onoff = (20,5), onoff_sec = None, warning_time = 30):
    if onoff_sec is None:
        onoff_sec = (onoff[0]*60, onoff[1]*60)
    #sleep until a minute is left
    chirp_start(piezo)
    _s = max(onoff_sec[0]-warning_time, 0)
    bad_sleep(_s)
    #chirp once for 1 minute warning
    chirp(piezo)
    bad_sleep(warning_time)
    #_music.play_from_file(piezo, './lib/my_tunes/ffvii_raw.txt', 99*2, switches, interrupt_time = onoff_sec[1])
    _music.play_from_file(piezo, './lib/my_tunes/zelda_raw.txt', 88, switches, interrupt_time = onoff_sec[1])    
    #play warning
    
    #play start
    pass

def make_border(splash):
    color_bitmap = displayio.Bitmap(W, H, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFFFFFF  # White

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)
    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(W-2, H-2, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x777777  # Black
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=1, y=1)
    splash.append(inner_sprite)

def make_bitmap(splash, fname):
    make_border(splash)
    color_bitmap = displayio.Bitmap(W, H, 1)
    color_palette = displayio.Palette(2)
    color_palette[0] = 0x000000  # Black
    color_palette[1] = 0xFFFFFF  # White

    bitmap = displayio.Bitmap(W, H, 1)
    
    row = 0
    with open(fname, 'r') as f:
        temp = f.readline()
        while temp:
            for idx, item in enumerate(temp.split(',')):
                bitmap[idx, row] = int(item)
            temp = f.readline()
            row+=1
    bg_sprite = displayio.TileGrid(bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)


piezo, W, H, display, splash, switches = setup()
make_bitmap(splash, 'lib/my_tunes/tomato.txt')

#_music.play_from_file(piezo, './lib/my_tunes/ffvii_raw.txt', 99*2, switches)
#pomodoro(onoff_sec = (10,4), warning_time = 5)

#_music.play_tune(piezo, _music._ffvii, _tempo= 99*2, interrupt_buttons = switches)
select = 0

timer = 0
button_0 = 0
prev_time = time.monotonic()

class Button():
    def __init__(self, switch):
        self.switch = switch
        self.time_down = 0
        self.state = 'off' #'tap', 'double (tap)', 'long'
        self.time_cool = 0
        self.pushes = []
    
    def __bool__(self):
        return self.switch.value
    
    def __iadd__(self, delta):
        self.time_down = self.time_down + delta
        pass
    
    def run(self):
        isdown = self.switch.value
        curr_time = time.monotonic()
        if len(self.pushes) == 0:
            self.pushes.append([isdown, curr_time])
            return
        
        prev_event, prev_time = self.pushes[-1]
        delta = curr_time - prev_time
        if delta> 8:
            self.state = "off"
            self.pushes = [[isdown, curr_time]]
            return
        if isdown and not prev_event:
            self.pushes.append([isdown, curr_time])
        elif not isdown and prev_event:
            self.pushes.append([isdown, curr_time])
            
        if len(self.pushes) < 2:
            pass #return
        if isdown and prev_event and delta>5:
            self.state = "long"
            self.pushes = [[isdown, curr_time]]
            return
        if isdown and not prev_event and delta > 3:
            self.state = "tap"
            self.pushes =[[isdown, curr_time]]
            return
        if isdown and not prev_event and delta < 3:
            if len(self.pushes) > 2:
                if self.pushes[-2]:
                    self.state = "double tap"
                    self.pushes =[[isdown, curr_time]]
                    return
            
        
        return
        if len(self.pushes) == 0:
            self.pushes.append([isdown, curr_time])
            return
        if isdown:
            prev_event, prev_time = self.pushes[-1]
            delta = curr_time - prev_time
            if prev_event and delta > 5:
                self.pushes = []
                self.state = 'long'
                return
            if not prev_event:
                self.pushes.append([isdown, curr_time])
            if len(self.pushes[-1]) < 3:
                return
            if self.pushes[-1] and not self.pushes[-2] and self.pushes[-3]:
                print('double check: ', self.pushes[-1][1]-self.pushes[-2][1])
                if self.pushes[-1][1]-self.pushes[-2][1] < 3:
                    self.state = 'double'
                    self.pushes = []
                    return
        else:
            prev_event, prev_time = self.pushes[-1]
            delta = curr_time - prev_time
            if prev_event and delta > 3:
                self.state = "tap"
                self.pushes = []
                return
            if len(self.pushes) < 3:
                if prev_event:
                    self.pushes.append([isdown, curr_time])
                return
            if self.pushes[-2] and delta > 3:
                assert False, 'asdf'
            if self.pushes[-2] and delta > 3:
                self.state = "tap"
                self.pushes = []
                return
            
        '''
        if isdown:
            self.time_down += delta
            if self.state == 'pretap':
                if self.time_cool >=0:
                    self.state = 'double'
                    return
            self.time_cool = 1
        else:
            if self.state == 'pretap':
                if self.time_cool <0:
                    self.state = 'tap'
                    return
            else:
                self.state = 'off'
            self.time_down = 0
            self.time_cool = self.time_cool-delta
            
        if self.time_down > 5:
            self.state = 'long'
            
        elif self.time_cool >= 0 and self.state == 'off':
            self.state = 'pretap'
        '''
        
        

S = Button(switches[0])

while True:
    curr_time = time.monotonic()
    delta = curr_time-prev_time
    S.run()
    print(S.state, S.pushes, len(S.pushes))
    if S.state != 'off':
        pass
    prev_time = time.monotonic()
    time.sleep(0.07)
    



