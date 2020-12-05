#!/usr/bin/env python3

import requests, json, os
from pathlib import Path
import datetime
import tweepy
from time import sleep

dir = Path(os.path.dirname(os.path.abspath(__file__)))

# Authenticate to Twitter
auth = tweepy.OAuthHandler("YOUR_OAUTH_HANDLER")
auth.set_access_token("YOUR_ACCESS_TOKEN")
api = tweepy.API(auth)

def get_new():
    #Structure: id, runner_id
    data = json.loads(requests.get("https://www.speedrun.com/api/v1/runs?status=verified&orderby=verify-date&direction=desc&max=200").text)

    runs = []

    with open(dir / 'run.txt', 'w') as f:
        print ("Getting new runs... ")
        for item in data["data"]:
            if item['level'] == None:
                print(item['id'])
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

                sub_cats = ""
                for value in run['values']:
                    print(str(value))
                    print(run['values'][value])
                    is_sub = str(json.loads(requests.get("https://www.speedrun.com/api/v1/variables/" + str(value)).text)['data']['is-subcategory'])
                    if is_sub == "True":
                        variable = json.loads(requests.get("https://www.speedrun.com/api/v1/variables/" + str(value)).text)['data']['values']['values']
                        #variable = json.loads(requests.get("https://www.speedrun.com/api/v1/variables/" + str(value)).text)['data']['values']['values'][str(value)]
                        print(str(variable))
                        sub_cats = sub_cats + " [" + variable[run['values'][value]]['label'] + "]"

                url =  json.loads(requests.get("https://www.speedrun.com/api/v1/runs/" + item).text)['data']['weblink']

                real = 0
                ingame = 0
                real_string = ""
                ingame_string = ""
                time_text = ""
                noloads = 0
                noloads_string = ""

                real = run['times']['realtime_t']
                if real > 0:
                    if '.' in str(real):
                        real_string = str(datetime.timedelta(seconds=real)).rstrip('0').lstrip('0:').replace(" day, ", "d")
                    else:
                        real_string = str(datetime.timedelta(seconds=real)).lstrip('0:').replace(" day, ", "d")

                ingame = run['times']['ingame_t']
                if ingame > 0:
                    if '.' in str(ingame):
                        ingame_string = str(datetime.timedelta(seconds=ingame)).rstrip('0').lstrip('0:')
                    else:
                        ingame_string = str(datetime.timedelta(seconds=ingame)).lstrip('0:')

                noloads = run['times']['realtime_noloads_t']
                if noloads > 0:
                    if '.' in str(noloads):
                        noloads_string = str(datetime.timedelta(seconds=noloads)).rstrip('0').lstrip('0:')
                    else:
                        noloads_string = str(datetime.timedelta(seconds=noloads)).lstrip('0:')


                if (ingame > 0 and real > 0):
                    time_text = real_string + " RTA, " + ingame_string + " IGT"
                    print(time_text)
                elif (ingame > 0 and real == 0):
                    time_text = ingame_string
                    print(time_text)
                elif (ingame == 0 and real > 0):
                    time_text = real_string
                    print(time_text)

                if (noloads > 0):
                    time_text = time_text + ", " + noloads_string + " (No Loads)"
                    print(time_text)

                with open(dir / 'jp_runs.txt', 'a') as f:
                    f.write((item + "\n"))

                api.update_status(game + " - " + category + sub_cats + " in " + time_text + " by " + users_text + " " + url)
        sleep(1)
    sleep(5)


#------------------------------------------------------------------#

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

new = get_new()
old = get_old()
fresh = compare(old, new)

send_runs()
sleep(5)
