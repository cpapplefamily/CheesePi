# Python code to run on a Raspberry Pi to interface with Cheesy Arena

# This is a work in proccess. Spelling errors and reliability issues still need to be addressed. 


This must be run using sudo and retaining user enviorment using the -E switch
Currently run using sudo -E Python3 cheesePi.py

## Runtime Options
'-a','--alliance', help="Alliance Coler [red,blue] default = red", default = 'red', type=str

'-c','--led_count', help="Total number of LED's -  default = 150", default = 150, type=int

'-p','--led_pin', help="GPIO pin LED connected to - default = 18", default = 18, type=int

'-s','--led_sol', help="How many Sign of Life LED to use - default = 1", default = 1, type=int

'-m','--led_max_score', help="Max power Cell Count - default = 30", default =30, type=int


I still need to compile a list of libraies that will need to be installed to use. The system 
This was developed on had many interations of projects built. After I install it on a fresh 
image I can try to inclued what needs to be installed.




