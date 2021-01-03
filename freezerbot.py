# MinusEightyBaby Twitter Bot

import socket
import time, sys
from daqhats import mcc134, hat_list, HatIDs, TcTypes
import tweepy

###### SET THESE VARIABLES
SLEEP_SECONDS = 10          # every 10 seconds
FRIDGE_LABEL = 'fridge_a'   # set a label for your fridge
CONSUMER_KEY = "XXX"        # change XXX to your Twitter Consumer Key
CONSUMER_SECRET = "XXX"     # change XXX to your Twitter Consumer Secret
ACCESS_TOKEN = "XXX"        # change XXX to your Twitter Access Token
ACCESS_SECRET = "XXX"       # change XXX to your Twitter Access Key
#######


channel = 0
tc_type = TcTypes.TYPE_T
tweet = ""
old_temp = 100.0
old_tweet = ""

def myPrint(text):
    with open("/home/pi/freezercheck/freezerbot.log", "a") as f:
        f.write(text + "\n")

# Tweet the current IP address.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    try:
        s.connect(("8.8.8.8", 80))
        myPrint("My address is " + s.getsockname()[0])
        s.close()
        break
    except:
        myPrint("Failed to connect to internet... will try again soon.")
        time.sleep(3.0)

# Find the MCC 134
hats = hat_list(filter_by_id=HatIDs.MCC_134)
if not hats:
    myPrint('No MCC 134 found, quiting')
    sys.exit()
else:
    myPrint('Found MCC134')

board = mcc134(hats[0].address)

# Configure the thermocouple type on the channel 0
board.tc_type_write(channel, tc_type)

while True:
    error = True
    temperature = board.t_in_read(channel)
    if temperature == mcc134.OPEN_TC_VALUE:
       # print('MC143 Error - Open')
        tweet = "Error - Open"
    elif temperature == mcc134.OVERRANGE_TC_VALUE:
       # print('MC143 Error - Over range')
        tweet = "Error - Over range"
    elif temperature == mcc134.COMMON_MODE_TC_VALUE:
       # print('MC143 Error - Common mode')
        tweet = "Error - Common Mode"
    else:
        error = False
        temp_val = "{:.2f}".format(temperature)
       # auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
       # auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
       # api = tweepy.API(auth)
       # api.update_status(status="%s is at %s" % (FRIDGE_LABEL, temp_val))
        tweet = temp_val
    if error:
        if tweet != old_tweet:
            myPrint(tweet)
            old_tweet = tweet
    elif temperature >= old_temp + 3.0 or temperature <= old_temp - 3.0:
        myPrint(tweet) 
        old_temp = temperature

    time.sleep(SLEEP_SECONDS)

