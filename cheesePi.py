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

last_matchstate = 0
total_cells = 0


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

FMS_IP = "10.0.100.05"
FMS_PORT = "8080"
FMS_SERVER = FMS_IP + ":" + FMS_PORT
ALLIANCE_COLOR = 'red' # Change accordingly
#ALLIANCE_COLOR = 'blue' # Change accordingly
USERNAME = 'root'
PASSWORD = 'root'

goal_char_msg_map = {
    "I": '{ "type": "CI" }',
    "O": '{ "type": "CO" }',
    "L": '{ "type": "CL" }'
}

#Global Counters
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

#Function to wait for a Power Cell to be scored
def get_power_cell_to_count():
    global innerCount
    global outerCount
    global lowerCount
    while(outerCount == 0 and innerCount == 0 and lowerCount == 0):
        one = 1
    return True

#Retrieve the keyStroke char for the goal to be tallied
def get_msg_from_goal_char(goal_char):
    return goal_char_msg_map[goal_char]

def blink_led():
    if GPIO.input(LED_Pin):
        #myfill(Color(255, 0, 0))
        RGB.strip_set_LED(0,RGB.LED_SOL,Color(63,63,63))
        GPIO.output(LED_Pin,0)
    else:
        #myfill(Color(0, 0, 255))
        RGB.strip_set_LED(0,RGB.LED_SOL,Color(255,255,255))
        GPIO.output(LED_Pin,1)
        


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
                        
    RGB.strip_control(ALLIANCE_COLOR, last_matchstate, total_cells) 
                        #strip_control(last_matchstate, total_cells)
                        #useable = strip.numPixels() - LED_SOL
                        #strip_set_LED(LED_SOL,strip.numPixels(),Color(0, 0, 0))
                        #strip_set_LED(LED_SOL,int(c/30*useable),get_aliance_color_RGB(ALLIANCE_COLOR))
                    

    
        


    
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
                
                if (goal_char in goal_char_msg_map):
                    print(f'Info: sent {get_msg_from_goal_char(goal_char)}')
                    try:
                        ws.send(get_msg_from_goal_char(goal_char))
                    except Exception:
                        open_websocket()
                else:
                    print('Error: unknown char received')

        thread.start_new_thread(run, ())
    
    return on_ws_open
    
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
    led_count = 100
    led_pin = 18
    led_sol = 1
    led_max_score = 30
    RGB.create_strip(100, 18, 1, 30,RGB.get_aliance_color_RGB(ALLIANCE_COLOR))
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
    main()
