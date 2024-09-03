import board
import pwmio
import displayio
import time
from digitalio import DigitalInOut, Direction, Pull
import _music
import time


# Compatibility with both CircuitPython 8.x.x and 9.x.x.
# Remove after 8.x.x is no longer a supported release.
try:
    from i2cdisplaybus import I2CDisplayBus
except ImportError:
    print('asdf')
    from displayio import I2CDisplay as I2CDisplayBus
    
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
        for f in :
            _break = any([x.value for x in ])
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


piezo, W, H, display, splash, switches = setup()
#_music.play_from_file(piezo, './lib/my_tunes/ffvii_raw.txt', 99*2, switches)
pomodoro(onoff_sec = (10,4), warning_time = 5)

#_music.play_tune(piezo, _music._ffvii, _tempo= 99*2, interrupt_buttons = switches)

while True:
    print([x.value for x in switches])
    time.sleep(0.1) 
    pass
