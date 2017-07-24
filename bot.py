import os
import tweepy
import json as js
from tweepy.streaming import StreamListener
import urllib3 as urll
from secrets import *
from time import gmtime, strftime, sleep

# ====== Authentication ===============
userhandle = "@AniHumane"
auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
api = tweepy.API(auth)


# ====== Individual bot configuration ==========================
bot_username = 'getmypnrstatus'
logfile_name = bot_username + ".log"

# ======= Links ============
checkpnrlink = "http://api.railwayapi.com/pnr_status/pnr/"#+pnr_no+"/apikey/"+RAIL_API+"/"
cancelledlink = "http://api.railwayapi.com/cancelled/date/"#26-12-2015/apikey/"+RAIL_API+"/"
routelink = "http://api.railwayapi.com/route/train/"#<train number>/apikey/<apikey>/"


class listener(StreamListener):
    def on_data(self, data):
        print("new tweet! \n")
        try:
            jsonData = js.loads(data)
            tweet_text = str(jsonData['text']).split(" ")
            print(tweet_text);
            if tweet_text[1] == "PNR":
                pnr_no = str(jsonData['text'])[-10:]
                api.update_status('@'+jsonData['user']['screen_name']+"\n"+getPNRstatus(pnr_no), jsonData['id'])

            print(tweet_text[1] == 'ROUTE')
            if tweet_text[1] == 'ROUTE':
                res = gettrainroute(tweet_text[2])
                print(res)
                api.update_status('@'+jsonData['user']['screen_name']+"\n"+res, jsonData['id'])

            return True
        except BaseException as e:
            print('FAILED ONDATA : '+str(e))
            sleep(5)

    def on_error(self, status):
        print(status)

def getPNRstatus(pnr_no):
    checkpnrlink += pnr_no+"/apikey/"+RAIL_API+"/"
    result = urll.urlopen(checkpnrlink).read()
    return result

def gettrainroute(trainno):
    routelink = "http://api.railwayapi.com/route/train/" + trainno + "/apikey/"+RAIL_API+"/"
    print(routelink)
    http = urll.PoolManager()
    result = http.request('GET',routelink)
    return result.data




def tweet(text):
    try:
        api.update_status(text)
    except tweepy.error.TweepError as e:
        log(e.message)
    else:
        log("Tweeted: " + text)


def log(message):
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)




if __name__ == "__main__":
    #tweet(tweet_text)
    mymentions = tweepy.Stream(auth, listener())
    mymentions.filter(track=[userhandle])