from rpi_ws281x import *
import time

# LED strip configuration:
strip = None
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    	= 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        	= 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS 	= 10     # Set to 0 for darkest and 255 for brightest
LED_INVERT     	= False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    	= 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
"""
These are only Default
The following can be over rode when constructing the LED Strip
"""
LED_COUNT      	= 300      # Number of LED pixels.
LED_PIN        	= 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_SOL		= 5		#Number of Sign Of Life LED's 
LED_MAX_SCORE  	= 30		# Power Cell Max Score


"""
stage:capacity
Stage 1
Stage 2-3

#Samle:
c = get_powercell_capacity_range(1,1)
print(c)
print(c[1])
"""
powercell_capacity_map = {
    1: {1: (14,17),
	2: (11,20),
	3: (9,22),
	4: (7,24),
	5: (5,26),
	6: (4,27),
	7: (3,28),
	8: (2,29),
	9: (1,30),
	10: (1,30),
	11: (1,30),
	12: (1,30),
	13: (1,30),
	14: (1,30),
	15: (1,30)},
    2: {1: (15,16),
	2: (14,17),
	3: (13,18),
	4: (12,19),
	5: (11,20),
	6: (10,21),
	7: (9,22),
	8: (8,23),
	9: (7,24),
	10: (6,25),
	11: (5,26),
	12: (4,27),
	13: (3,28),
	14: (2,29),
	15: (1,30)},
    3: {1: (15,16),
	2: (14,17),
	3: (13,18),
	4: (12,19),
	5: (11,20),
	6: (10,21),
	7: (9,22),
	8: (8,23),
	9: (7,24),
	10: (6,25),
	11: (5,26),
	12: (4,27),
	13: (3,28),
	14: (2,29),
	15: (1,30)}
}

field_color_map = {
    "green": Color(0,255,0),
    "violet": Color(150,0,150),
    "yellow": Color(255,255,0)
}

aliance_colors_map = {
    "red": Color(255, 0, 0),
    "green": Color(0, 255, 0),
    "blue": Color(0, 0, 255)
}

"""
Create a RGB LED Strip with over ride values
"""
def create_strip(led_count, led_pin, led_sol, max_score,color):
    global LED_COUNT
    global LED_PIN
    global LED_SOL
    global LED_MAX_SCORE
    LED_COUNT = led_count
    LED_PIN = led_pin
    LED_SOL = led_sol
    LED_MAX_SCORE = max_score
    create_default_strip(color)
    
"""
Create the RGB LED Strip
"""
def create_default_strip(color):
    global strip
    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    for i in range(0,strip.numPixels(),4):
        strip.setPixelColor(i, color)
        strip.setPixelColor(i+1, Color(0,0,0))
        strip.setPixelColor(i+2, Color(0,0,0))
        strip.setPixelColor(i+3, Color(0,0,0))
    strip.show()
   
"""
Helpers to get variables
"""
def get_powercell_capacity_range(stage, capacity):
    return powercell_capacity_map[stage][capacity]

def get_field_color_RGB(status_color):
    return field_color_map[status_color]
    
def get_aliance_color_RGB(alliance_color):
    return aliance_colors_map[alliance_color]
	
"""
Fill Strip with given Color
Acnolaging the Sign Of Life LED's
"""
def strip_set_LED(startLED, lastLED, color):
    if lastLED > strip.numPixels():
	    lastLED = strip.numPixels()
    for i in range(startLED,lastLED):
	    strip.setPixelColor(i, color)
    strip.show()
    
"""
Fill Entire Strip with given Color
"""
def strip_fill(color):
    print("myFill enter")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

"""
This Defenition is called after each message to set the LED depending on the field State
"""
def strip_control(alliance_color, matchstate, total_cells):
    if matchstate == 0: #post match
        strip_set_LED(LED_SOL,strip.numPixels(),get_field_color_RGB("green"))
    elif matchstate == 1:
        #prematch
        strip_set_LED(LED_SOL,strip.numPixels(),Color(0, 0, 0))
    elif matchstate == 2:
        #prematch
        strip_set_LED(LED_SOL,strip.numPixels(),Color(0, 0, 0))
    elif matchstate == 3:
        #auto
        if total_cells > LED_MAX_SCORE:
            theaterChase(alliance_color)
        else:
            LED_Score(alliance_color, total_cells)
    elif matchstate == 4:
        #pause
        if total_cells > LED_MAX_SCORE:
            theaterChase(alliance_color)
        else:
            LED_Score(alliance_color, total_cells)
    elif matchstate == 5:
        #teleop
        if total_cells > LED_MAX_SCORE:
            theaterChase(alliance_color)
        else:
            LED_Score(alliance_color, total_cells)
    elif matchstate == 6:
        #post match
        strip_set_LED(LED_SOL,strip.numPixels(),get_field_color_RGB("violet"))
    else:
        pass

"""
Simple Fill Strip from the start to the End by the percentage of scored
"""	
def LED_Score(alliance_color, total_cells):
    useable = strip.numPixels() - LED_SOL
    """ Fill strip with Percentage relitive to max"""
    for i in range(LED_SOL,int(total_cells/LED_MAX_SCORE*useable)):
        strip.setPixelColor(i, get_aliance_color_RGB(alliance_color))
    """ Fill remaining strip off"""
    if int(total_cells/LED_MAX_SCORE*useable)<LED_SOL:
        blankStart = LED_SOL
    else:
        blankStart = int(total_cells/LED_MAX_SCORE*useable)
    for i in range(blankStart,LED_COUNT):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

"""
start of Marque
Currently does not animate. Will need to revisit making sure we don't block the code
"""	
def theaterChase(alliance_color):
    """Movie theater light style chaser animation."""
    for i in range(LED_SOL, strip.numPixels(), 2):
        strip.setPixelColor(i, get_aliance_color_RGB(alliance_color))
    for i in range(LED_SOL, strip.numPixels(), 2):
        strip.setPixelColor(i+1, Color(100,100,100))
    
    strip.show()        
      
      
"""
Debug Code
"""
def printFieldState(matchstate):
    print('************************')
    print(f'MatchStatus: {get_matchStatus_txt(matchstate)}')
    print('************************')
