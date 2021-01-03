# MinusEightyBaby Twitter Bot

import socket
import time, sys
import datetime
from random import randrange
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

jokes = [
    ("A duck walks up to a checkout counter to purchase a condom.  The checkout "
    "clerk asks, \"How would you like to pay for that?\"  The duck says, \"Just "
    "put it on my bill.\""),
    "Please write a new joke!"
]

channel = 0
tc_type = TcTypes.TYPE_T
tweet = ""
old_temp = 100.0
old_tweet = ""

def log(text):
    with open("/home/pi/freezercheck/freezerbot.log", "a") as f:
        today = datetime.datetime.today()
        time_string = today.strftime("%m/%d/%Y, %H:%M:%S")
        f.write(time_string + ": " + text + "\n")

def sendTweet(text):
    log(text)
    # Send tweet here.
    # auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    # auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    # api = tweepy.API(auth)
    # api.update_status(status="%s is at %s" % (FRIDGE_LABEL, temp_val))

def findMacAddress():
    """Find the current local MAC address.  Retry until success.
       Since this script is called during boot, it may have to
       retry a few times until the network stack comes up."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            s.connect(("8.8.8.8", 80))
            macAddress = s.getsockname()[0]
            s.close()
            return macAddress
        except:
            log("Failed to connect to internet... will try again soon.")
            time.sleep(5.0)

def tweetRandomJoke():
    joke = jokes[randrange(len(jokes))]
    temperature = board.t_in_read(channel)
    temp_val = "%.2f" % temperature
    sendTweet(joke + "  Curreent temp is " + temp_val)

tweeted_joke = False

def printJokeMondayAtNoon():
    """Print a random joke each Monday at noon."""
    global tweeted_joke
    today = datetime.datetime.today()
    weekday = today.weekday()
    hour = today.time().hour
    if weekday == 0 and hour == 12:
        # Tweet a random joke at noon on Monday.
        if not tweeted_joke:
            tweetRandomJoke()
            tweeted_joke = True
    else:
        tweeted_joke = False

# Tell the world that we've booted and how to connect over ssh.  To login, use:
# ssh pi@xxx.xxx.xxx, where xxx.xxx.xxx is the MAC address from the tweet.
sendTweet("Booted with MAC address " + findMacAddress())

# Find the MCC 134
hats = hat_list(filter_by_id=HatIDs.MCC_134)
if not hats:
    sendTweet('No MCC 134 found, quiting')
    sys.exit()
else:
    log('Found MCC134')

board = mcc134(hats[0].address)

# Configure the thermocouple type on the channel 0
board.tc_type_write(channel, tc_type)

while True:
    printJokeMondayAtNoon()
    error = True
    temperature = board.t_in_read(channel)
    if temperature == mcc134.OPEN_TC_VALUE:
        tweet = "Error - Open"
    elif temperature == mcc134.OVERRANGE_TC_VALUE:
        tweet = "Error - Over range"
    elif temperature == mcc134.COMMON_MODE_TC_VALUE:
        tweet = "Error - Common Mode"
    else:
        error = False
        temp_val = "%.2f" % temperature
        tweet = temp_val
    if error:
        if tweet != old_tweet:
            sendTweet(tweet)
            old_tweet = tweet
    elif temperature >= old_temp + 3.0 or temperature <= old_temp - 3.0:
        sendTweet(tweet) 
        old_temp = temperature
    time.sleep(SLEEP_SECONDS)
