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

class Joke:

    def __init__(self):
        self.tweeted_joke = False
        self.count = 0;
        self.jokes = [
        ("What has two eyes, six ears, and multiple spleens?"
        "\n\nThis freezer." 
        "\n\nIn case you were wondering, there’s a bag of coyote ears on shelf 3."),
        
        ("Why did the chicken get into the freezer?"
        "\n\nTo get to the other side."),

        ("What’s the difference between a dog and a marine biologist?"
        "\n\nOne wags a tail and the other tags a whale."),

        ("Biology is the only science where multiplication is the same thing as division."),

        ("Why did the bear dissolve in water?"
        "\n\nIt was polar."),

        ("Why was the function so bent out of shape?"
        "\n\nIts regression model was too tight a fit."),

        ("How does a physicist deal with a long to-do list?"
        "\n\nBy truncating it after the first three terms."),

        ("Why do biologists use the abbreviation MAT?"
        "\n\nSaying the whole thing is a micro-annunciation test."
        "\n\n (I'm well aware that this is the dumbest one yet, but YOU have the power to fix this."
        "Send me science jokes. It's never too late.)"),

        ("Stop saying \"rabies-vaccinated,\" and start saying \"raccoon-immune.\""),

        ("Why did the mathematician name his dog Cauchy?"
        "\n\nBecause he left a residue at every pole."),

        ("Just saw a great film about databases — can’t wait for the SQL."),

        ("A plane was about to take off from Warsaw to England when the captain realized"
        "there was a problem that would cause the plane to become unstable in the air and crash."
        "Luckily, he knew how to fix it: he got on the intercom and asked the Poles to move to"
        "the left half plane."),

        ("An atom and another atom are talking to each other. One atom says, \"I lost an electron.\""
        "The other replies, \"No way, are you positive?\""),

        ("This was going to be a joke about sodium… but Na."),

        ("Feeling more negative than usual? Disconnected from others? Like you’re just not grounded anymore?"
        "\n\nYou’re not alone. Every year, thousands of students struggle with charging by induction.")
    ]

    def tweetJoke(self):
        joke = self.jokes[self.count]
        temperature = board.t_in_read(channel)
        temp_val = "%.2f" % temperature
        sendTweet(joke + "  Curreent temp is " + temp_val)
        print(joke)

    def printJokeMondayAtNoon(self):
        today = datetime.datetime.today()
        weekday = today.weekday()
        hour = today.time().hour
        #if weekday == 0 and hour == 12:
        if not self.tweeted_joke:
            # Tweet a joke at noon on Monday.
            if not self.tweeted_joke:
                self.tweetJoke()
                self.tweeted_joke = True
                if self.count < len(self.jokes):
                    self.count += 1
                else:
                    self.count = 0

        else:
            self.tweeted_joke = False




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

# Create new joke instance
weeklyJoke = Joke()

while True:
    weeklyJoke.printJokeMondayAtNoon()
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
