#!/usr/bin/env python3

import requests, json, os
from pathlib import Path
import datetime
import tweepy
from time import sleep

dir = Path(os.path.dirname(os.path.abspath(__file__)))

# Authenticate to Twitter, insert access information
auth = tweepy.OAuthHandler("", "")
auth.set_access_token("", "")
api = tweepy.API(auth)

def get_new():
    #Structure: id, runner_id
    data = json.loads(requests.get("https://www.speedrun.com/api/v1/runs?status=verified&orderby=verify-date&direction=desc&max=200").text)

#----- TEST START
#    with open(dir / 'test.txt', 'r') as f:
#        data = json.loads(f.read())
#----- TEST END
        
    runs = []
    
    with open(dir / 'run.txt', 'w') as f:
        print ("Getting new runs... ")
        for item in data["data"]:
            runs.append(item['id'])
            f.write(item['id'] + "\n")
        f.write("\n")
    runs.reverse()
    return runs

def get_old():
    runs = []
    print ("Getting old runs... ")
    with open(dir / 'run_old.txt', 'r') as f:
        for line in f:
            if len(line) > 5:
                runs.append(line[:len(line)-1])
    return runs


def compare(old, new):
    fresh = []
    print ("New runs: ")
    with open(dir / 'run_old.txt', 'a') as f:
        for item in new:
            if item not in old:
                print("New: " + item)
                fresh.append(item)
                f.write(item + "\n")
    if len(fresh) == 0:
        print("No new runs")
        raise SystemExit(0)
    return fresh


def send_runs():
    run = []

    for item in fresh:
        run = json.loads(requests.get("https://www.speedrun.com/api/v1/runs/" + item).text)['data']

        users = []
        is_japanese = False
        
        for user in run['players']:
            try:
                user_data = json.loads(requests.get("https://www.speedrun.com/api/v1/users/" + user['id']).text)['data']
            except KeyError:
                is_japanese = False
            else:
                try:
                    if str(user_data['location']['country']['code']) == "jp":
                        print("japan hype ", user_data['names']['japanese'])
                        if user_data['names']['japanese'] != None:
                            users.append(user_data['names']['japanese'])
                            #print("JP_jp: " + user_data['names']['japanese'])
                        else:
                            users.append(user_data['names']['international'])
                            print("JP_int: " + user_data['names']['international'])
                        is_japanese = True
                    else:
                        print(user_data['location']['country']['code'] + ": " + user_data['names']['international'])
                except:
                    is_japanese = False

        if is_japanese:
            print("Start is_japanese loop")
            users_text = ""
            try:
                for user in users:
                    users_text = users_text + ", " + user
                users_text = users_text[2:]
            except: #NoneType
                    print("NoneType Error")
                    break

            if users_text is not "":
                game_data = json.loads(requests.get("https://www.speedrun.com/api/v1/games/" + run['game']).text)['data']
                #print(game_data['names']['japanese'])
                if game_data['names']['japanese'] is not None:
                    game = game_data['names']['japanese']
                else:
                    game = game_data['names']['international']
                
                category = json.loads(requests.get("https://www.speedrun.com/api/v1/categories/" + run['category']).text)['data']['name']

                url =  json.loads(requests.get("https://www.speedrun.com/api/v1/runs/" + item).text)['data']['weblink']
               
                real = 0
                ingame = 0
                real_string = ""
                ingame_string = ""
                time_text = ""
                
                real = int(run['times']['realtime_t'])
                if real > 0:
                    real_string = str(datetime.timedelta(seconds=real))
                ingame = int(run['times']['ingame_t'])
                if ingame > 0: 
                    ingame_string = str(datetime.timedelta(seconds=ingame))

                if (ingame > 0 and real > 0):
                    time_text = real_string + " RTA, " + ingame_string + " IGT"
                    print(time_text)
                elif (ingame > 0 and real == 0):
                    time_text = ingame_string
                    print(time_text)
                elif (ingame == 0 and real > 0):
                    time_text = real_string
                    print(time_text)

#                print ("Game: " + game)
#               print ("Category: " + category)
#                print ("Player: " + users_text)
#                print ("Time: " + time_text)
                print ("URL: " + url)

                with open(dir / 'jp_runs.txt', 'a') as f:
                    f.write((item + "\n"))
#                with open(dir / 'jp_detail.txt', 'a') as f:
#                    f.write(("Game: " + game + "\n" + "Category: " + category + "\n" + "Player: " + users_text + "\n" + "Time: " + time_text + "\n" + "URL: " + url + "\n\n" ).encode())

                api.update_status(game + " - " + category + " in " + time_text + " by " + users_text + ": " + url)
        sleep(2)
    sleep(5)

                                       
#------------------------------------------------------------------#

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")
    
new = get_new() # fetch a list [] #new = get_new_test()
old = get_old()
fresh = compare(old, new)
#for run in new:
#    print(run)

sleep(5)

send_runs()
