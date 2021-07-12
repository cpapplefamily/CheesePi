import os
import requests
import time
import _thread as thread
import websocket
import RPi.GPIO as GPIO
import json
import argparse
import cheesePowerPortRGB as RGB
from rpi_ws281x import Color

"""
Global Variables to track
Field State and power Cells
"""
last_matchstate = 0
total_cells = 0

"""
Set up GPIO
"""
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

"""
Constans
"""
FMS_IP = "10.0.100.05"
FMS_PORT = "8080"
FMS_SERVER = FMS_IP + ":" + FMS_PORT
ALLIANCE_COLOR = None #default red changed using runtime argument
USERNAME = 'root'
PASSWORD = 'root'


"""
Map all the Modes of the Field
"""
matchStatus_map = {
	0: "Feild Safe",
	1: "pre match",
	2: "pre match",
	3: "in Auto",
	4: "Pause After Auto",
	5: "in match",
	6: "Match Complete"
}

"""
Map Key Stroke Sets
AUTO: Add Score to the Auto
Teleop: Add Score to the Teleop
UNKNOWN: This was the Keystrokes use when we did not have game status in PI. 
        If using a Modified Fork of Cheesy arena that detects these inputs it
        will add the appreate counter
"""
goal_basic_char_msg_map = {
    "AUTO": {"I": '{ "type": "W" }',
             "O": '{ "type": "S" }',
             "L": '{ "type": "X" }'
            },
    "TELEOP": {"I": '{ "type": "R" }',
               "O": '{ "type": "F" }',
               "L": '{ "type": "V" }'
            },
    "UNKNOWN": {"I": '{ "type": "CI" }',
               "O": '{ "type": "CO" }',
               "L": '{ "type": "CL" }'
            }
}

#Global internal Counters
innerCount = 0
outerCount = 0
lowerCount = 0

#opto Issolator Channle to GPIO_Pin
optoIssolator_1 = 7
optoIssolator_2 = 11
optoIssolator_3 = 13
optoIssolator_4 = 15

#GPIO Assignments
innerCount_Pin = optoIssolator_1
outerCount1_Pin = optoIssolator_2
outerCount2_Pin = optoIssolator_3
lowerCount_Pin = optoIssolator_4

LED_Pin = 32

GPIO.setup(LED_Pin,GPIO.OUT)
GPIO.output(LED_Pin,0)

"""
Call Back functions
"""
###############################
## Inerner Count Input setup ##
###############################
GPIO.setup(innerCount_Pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def inner_callback(channel):
    global innerCount
    innerCount += 1
    
GPIO.add_event_detect(innerCount_Pin,GPIO.RISING,callback=inner_callback, bouncetime=200)

##############################
## Outer Count1 Input setup ##
##############################
GPIO.setup(outerCount1_Pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def outer1_callback(channel):
    global outerCount
    outerCount += 1
    
GPIO.add_event_detect(outerCount1_Pin,GPIO.RISING,callback=outer1_callback, bouncetime=200)

##############################
## Outer Count2 Input setup ##
##############################
GPIO.setup(outerCount2_Pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def outer2_callback(channel):
    global outerCount
    outerCount += 1
    
GPIO.add_event_detect(outerCount2_Pin,GPIO.RISING,callback=outer2_callback, bouncetime=200)

#############################
## Lower Count Input setup ##
#############################
GPIO.setup(lowerCount_Pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def lower_callback(channel):
    global lowerCount
    lowerCount += 1
    
GPIO.add_event_detect(lowerCount_Pin,GPIO.RISING,callback=lower_callback, bouncetime=200)


"""
Helpers to get variables
"""
#Function to wait for a Power Cell to be scored
def get_power_cell_to_count():
    global innerCount
    global outerCount
    global lowerCount
    while(outerCount == 0 and innerCount == 0 and lowerCount == 0):
        one = 1
    return True
    
#Retrieve the keyStroke Set for the goal to be tallied
def get_charset_from_basic_goal(matchState):
    return goal_basic_char_msg_map[matchState]
    
#Retrieve the keyStroke char for the goal to be tallied
def get_msg_from_basic_goal_char(matchState, goal_char):
    return goal_basic_char_msg_map[matchState][goal_char]
    
"""
Sign of Life
Blinks a GPIO pin as well as a presellected count of the RGB LED to 
show Communications are active to Cheesy Arena
Flip Flop on every MSG recieved
"""
def blink_led():
    if GPIO.input(LED_Pin):
        #RGB.strip_fill(Color(255, 0, 0))
        RGB.strip_set_LED(0,RGB.LED_SOL,Color(63,63,63))
        GPIO.output(LED_Pin,0)
    else:
        #RGB.strip_fill(Color(0, 0, 255))
        RGB.strip_set_LED(0,RGB.LED_SOL,Color(255,255,255))
        GPIO.output(LED_Pin,1)
        

"""
Parse's the MSG recieved
"""
def ws_msg(self, msg):
    global last_matchstate
    global total_cells
    blink_led()
    j = json.loads(msg)
    print(f"MSG Type {j['type']}")
    if j['type'] == "matchTime":
        #print("Is MatchTime") 
        if "data" in j:
            #print("data")
            d = j['data']
            #print(d)
            if "MatchState" in d:
                m_state = d['MatchState']
                if m_state == 0 and m_state != last_matchstate:
                    last_matchstate = m_state
                elif m_state == 1 and m_state != last_matchstate:                    
                    last_matchstate = m_state
                    #strip_control(last_matchstate, total_cells)                    
                elif m_state == 2 and m_state != last_matchstate:                    
                    last_matchstate = m_state
                    #strip_control(last_matchstate, total_cells)                    
                elif m_state == 3 and m_state != last_matchstate:                    
                    last_matchstate = m_state
                    #strip_control(last_matchstate, total_cells)                    
                elif m_state == 4 and m_state != last_matchstate:                    
                    last_matchstate = m_state
                    #strip_control(last_matchstate, total_cells)                    
                elif m_state == 5 and m_state != last_matchstate:
                    last_matchstate = m_state
                    #strip_control(last_matchstate, total_cells)                    
                elif m_state == 6 and m_state != last_matchstate:                    
                    last_matchstate = m_state
                    #strip_control(last_matchstate, total_cells)                    
                else:
                    last_matchstate = m_state
                    #strip_control(last_matchstate, total_cells)
                    
    else:
        if j['type'] == "realtimeScore":
            #print("Is RealtimeScore") 
            if "data" in j:
                #print("data")
                d = j['data']
                if "ScoreSummary" in d["Red"]:
                    x = d["Red"]
                    s = x['ScoreSummary']
                    if "TotalCells" in s:
                        total_cells = s["TotalCells"]
                        print(f"Total Power Cells:           {c}")
    # Update RGB LED Strip                    
    RGB.strip_control(ALLIANCE_COLOR, last_matchstate, total_cells) 

"""
Create the Thread that handle all the WebSocket actions
"""    
def get_on_ws_open_callback():
    def on_ws_open(ws):
        print("Connected to FMS")

        def run(*args):
            while(True):
                global innerCount
                global outerCount
                global lowerCount
                #Check for any counters that need to be tallied
                sendData = get_power_cell_to_count()
                #What Counter?
                if last_matchstate < 3:
                    outerCount == 0
                    innerCount == 0
                    lowerCount
                if (outerCount > 0):
                    goal_char = "O"
                    outerCount -= 1
                elif (innerCount > 0):
                    goal_char = "I"
                    innerCount -= 1
                elif (lowerCount > 0):
                    goal_char = "L"
                    lowerCount -= 1
                else:
                    print("nothing to Score")
                    goal_char = ""
                    
                    
                print(f'Info: received "{goal_char}"')
                
                """
                Get the Current Match State Char Map
                ie: AUTO or TELEOP
                """
                if (last_matchstate >= 3 and last_matchstate < 5):
                        matchState = "AUTO"
                elif (last_matchstate >= 5 and last_matchstate < 6):
                        matchState = "TELEOP"
                else:
                        matchState = "UNKNOWN"
                        
                mode = get_charset_from_basic_goal(matchState)
               
                """
                If Valid then send KeyStroke
                """
                if (goal_char in mode):
                    print(f'Info: sent {get_msg_from_basic_goal_char(matchState, goal_char)}')
                    try:
                        ws.send(get_msg_from_basic_goal_char(matchState, goal_char))
                    except Exception:
                        open_websocket()
                else:
                    print('Error: unknown char received')

        thread.start_new_thread(run, ())
    
    return on_ws_open
    
"""
Open up a Websocket to Cheesy Arena
"""
def open_websocket():
    def reopen_websocket():
        print("attempt to ReOpen Websocket")
        open_websocket()
    
    print("request.post")
    res = requests.post(f'http://{FMS_SERVER}/login'
        , data={'username': USERNAME, 'password': PASSWORD}
        , allow_redirects=False
    )
        
    print("Create ws")
    ws = websocket.WebSocketApp(f'ws://{FMS_SERVER}/panels/scoring/{ALLIANCE_COLOR}/websocket'
        , on_message = ws_msg
        , on_open=get_on_ws_open_callback()
        , on_close=reopen_websocket
        , cookie="; ".join(["%s=%s" %(i, j) for i, j in res.cookies.get_dict().items()])
    )

    #websocket.enableTrace(True)
    
    print("Run Forever")
    ws.run_forever()
    

def main():
    """Loops until a connection is made to the FMS.
    When connected opens a websocket 
    """
    led_count = 150
    led_pin = 18
    led_sol = 1
    led_max_score = 30
    RGB.create_strip(led_count, led_pin, led_sol, led_max_score,RGB.get_aliance_color_RGB(ALLIANCE_COLOR))
    #RGB.create_default_strip(RGB.get_aliance_color_RGB(ALLIANCE_COLOR))
    
    #Wait for Network connection to FMS
    while(True):
        print(f'Check Network Connection {FMS_IP}')
        response = os.system("ping -c 1 " + FMS_IP)
        if response == 0:
            print(f'{FMS_IP} Found')
        else:
            print("Network Error")
        if(response == 0): break
        time.sleep(2)
    time.sleep(1)
    print("Open Web Socket")
    open_websocket()
    
    
if __name__ == "__main__":
    # Init Process arguments
    parser = argparse.ArgumentParser(
        description = "Cheesy Arena Power Port Scoring Module"
    )
    
    # Optional Arguments
    parser.add_argument('-a','--alliance', help="Alliance Colr", default = 'red', type=str)
    
    args = parser.parse_args()
    
    if (args.alliance.lower() == 'blue'):
        print('Set to blue')
        ALLIANCE_COLOR = args.alliance.lower()
    elif (args.alliance.lower() == 'red'):
        print('Set to red')
        ALLIANCE_COLOR = args.alliance.lower()
    else:
        print('Invalid Color input! Set to default red')
        ALLIANCE_COLOR = 'red'
    
    main()
