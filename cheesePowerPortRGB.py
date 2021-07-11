from rpi_ws281x import *

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


matchStatus_map = {
	0: "Feild Safe",
	1: "pre match",
	2: "pre match",
	3: "in Auto",
	4: "Pause After Auto",
	5: "in match",
	6: "Match Complete"
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
    
def get_matchStatus_txt(status):
	return matchStatus_map[status]
	
def get_field_color_RGB(status_color):
    return field_color_map[status_color]
    
def get_aliance_color_RGB(alliance_color):
    return aliance_colors_map[alliance_color]
	
def strip_set_LED(startLED, lastLED, color):
	if lastLED > strip.numPixels():
		lastLED = strip.numPixels()
	for i in range(startLED,lastLED):
		strip.setPixelColor(i, color)
	strip.show()
    
def myfill(color):
    print("myFill enter")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def strip_control(alliance_color, matchstate, total_cells):
	#printFieldState(matchstate)
	if matchstate == 0:
		strip_set_LED(LED_SOL,strip.numPixels(),get_field_color_RGB("green"))
	elif matchstate == 1:
		strip_set_LED(LED_SOL,strip.numPixels(),Color(0, 0, 0))
	elif matchstate == 2:
		strip_set_LED(LED_SOL,strip.numPixels(),Color(0, 0, 0))
	elif matchstate == 3:
		strip_set_LED(LED_SOL,strip.numPixels(),get_field_color_RGB("yellow"))
	elif matchstate == 4:
		pass
		#strip_set_LED(LED_SOL,strip.numPixels(),Color(0, 0, 0))
	elif matchstate == 5:
		if total_cells > LED_MAX_SCORE:
			theaterChase(alliance_color)
		else:
			LED_Score(alliance_color, total_cells)
	elif matchstate == 6:
		strip_set_LED(LED_SOL,strip.numPixels(),get_field_color_RGB("violet"))
	else:
		pass
	
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
	
def theaterChase(alliance_color):
    """Movie theater light style chaser animation."""
    for i in range(LED_SOL, strip.numPixels(), 2):
        strip.setPixelColor(i, get_aliance_color_RGB(alliance_color))
    for i in range(LED_SOL, strip.numPixels(), 2):
        strip.setPixelColor(i+1, Color(100,100,100))
    
    strip.show()

def xtheaterChase(alliance_color):
    """Movie theater light style chaser animation."""
    for q in range(3):
        for i in range(LED_SOL, strip.numPixels(), 3):
            strip.setPixelColor(i+q, get_aliance_color_RGB(alliance_color))
        strip.show()
        for i in range(LED_SOL, strip.numPixels(), 3):
            strip.setPixelColor(i+q, 0)
            
            
def printFieldState(matchstate):
	print('************************')
	print(f'MatchStatus: {get_matchStatus_txt(matchstate)}')
	print('************************')
