import requests
import json
import pickle

import pandas as pd
import numpy as np
import random

from datetime import datetime
import time

cookie = {'steamLoginSecure': '76561198071584305%7C%7C3A8F0AB8B591CD5A91DA8F78E21F932DAB553855'}

game = 730
weaponList = ['Pistol', 'SMG', 'Rifle', 'SniperRifle', 'Shotgun', 'Machinegun', 'Knife']
weaponList = ['Pistol']

for weapon in weaponList:
    print(weapon)
    # itialize
    allItemNames = []
    allPages = []
    
    # find total number items
    # allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid=' + gameID + '&norender=1&count=100', cookies=cookie); # get page
    marketLink = "https://steamcommunity.com/market/search/render/"
    requestParams = {
		"query": "",
		"start": 1,
		"count": 1000,
		"search_descriptions": 0,
		"sort_column": "name",
		"sort_dir": "asc",
		"appid": game,
		"category_730_ItemSet[]": "any",
		"category_730_ProPlayer[]": "any",
		"category_730_StickerCapsule[]": "any",
		"category_730_TournamentTeam[]": "any",
		"category_730_Weapon[]": "any",
        "category_730_Type[]": f'tag_CSGO_Type_{weapon}',
		"norender": 1
	}
    
    weaponGet = requests.get(marketLink, requestParams, cookies=cookie)

    allItems = weaponGet.content; # get page content
    
    allItems = json.loads(allItems); # convert to JSON
    totalItems = allItems['total_count']; # get total count
    print(allItems)
    print(totalItems)

    # you can only get 100 items at a time (despite putting in count= >100)
    # so we have to loop through in batches of 100 to get every single item name by specifying the start position
    # for currPos in range(0,totalItems + 100,100): # loop through all items
    for currPos in range(0, totalItems+100, 100):
        # time.sleep(random.uniform(0.5, 2.5)) # you cant make requests too quickly or steam gets mad
        # time.sleep(.) # you cant make requests too quickly or steam gets mad
        requestParams['start'] = currPos
        print(currPos)
        
        # get item name of each
        weaponGet = requests.get(marketLink, requestParams, cookies=cookie)
        print('Items ' + str(currPos) + ' out of ' + str(totalItems) + ' ' + str(weaponGet.status_code)) # reassure us the code is running and we are getting good returns (code 200)
        

        allItems = weaponGet.content
        allItems = json.loads(allItems)
        allItems = allItems['results']
        for currItem in allItems: 
            allItemNames.append(currItem['hash_name']) # save the names
            print(currItem['hash_name'])
        
        allPages.extend(allItems)
        
        if currPos == 300:
            print('breaking')
            break
            
    
    ## remove duplicate items
    allItemNames = list(set(allItemNames))
    print(allPages)
    # quit()
    # Save all the name so we don't have to do this step anymore
    # use pickle to save all the names so i dont have to keep running above code
    with open(weapon + 'ItemNames.txt', 'w') as file:
        json.dump(allPages, file, ensure_ascii=True)
    print(allPages)
    print('test')
    print(file)
    
for weapon in weaponList:
    # open file with all names
    with open(weapon + 'ItemNames.txt', "rb") as file:   # Unpickling
       allItemNames = json.load(file)
    
    # intialize our Panda's dataframe with the data we want from each item
    weapon_df = pd.DataFrame(allItemNames)
    currRun = 1 # to keep track of the program running
    print(weapon_df)
    weapon_df.to_csv('Pistols.csv')