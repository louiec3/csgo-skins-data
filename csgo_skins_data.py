import requests
import json
import pickle

import pandas as pd
import numpy as np
import random

from datetime import datetime
import time

# pd.options.display.max_colwidth = 100

cookie = {'steamLoginSecure': '76561198071584305%7C%7CAF6E46BDEE06507FFA4148C70AE3CC9CB9FF47DB'}

game = '730'
weaponList = ['Pistol', 'SMG', 'Rifle', 'SniperRifle', 'Shotgun', 'Machinegun', 'Knife']
# weaponList = ['Knife']

def loop_pages():
    for weapon in weaponList:
        print(weapon)
        # itialize
        allItemNames = []
        allPages = []
        weaponsDataframes = []
        
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
        # print(allItems)
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
                
        ## remove duplicate items
        allItemNames = list(set(allItemNames))
        # print(allPages)

        # Save all the name so we don't have to do this step anymore
        # save all the names so i dont have to keep running above code
        with open(weapon + 'Items.txt', 'w') as file:
            json.dump(allPages, file, ensure_ascii=True)

    for weapon in weaponList:
        # add json data for each file to list to then create a dataframe
        with open(weapon + 'Items.txt', "rb") as file:
            allItemNames = json.load(file)
            weapon_df = pd.DataFrame(allItemNames)
            weaponsDataframes.append(weapon_df)

        # intialize our Panda's dataframe with the data we want from each item
        # weapon_df = pd.DataFrame(allItemNames)
        # currRun = 1 # to keep track of the program running
        # print(weapon_df)
        # weapon_df.to_csv(weapon + '.csv', index=False, encoding='utf-8-sig')
    allWeapons_df = pd.concat(weaponsDataframes)
    allWeapons_df.to_csv('AllWeapons.csv', index=False, encoding='utf-8-sig')

# loop_pages()


def clean_unicode(df):
    # use function if UTF not working
    # df.replace(to_replace={
    #             'name':{'â„¢':'™'}, 
    #             'hash_name':{'â„¢':'™'},
    #                 })

    charsDict = {
        ' ': '%20',
        '\|': '%7C',
        '\'': '%27',
        '\(': '%28',
        '\)': '%29',
        'é¾çŽ‹': '龍王',
        'Ã¶': 'ö',
        'â˜…': '★',
        'â™¥': '♥'
    }

    df['html_name'] = df['name'].replace(charsDict, regex=True)
    ## use market_hash_name for the future and move function to be used after the merged dataframe is created

    return df

# clean_unicode()


def expand_descriptions():
    df = pd.read_csv('AllWeapons.csv')
    
    df = clean_unicode(df)
    
    # print(df)
 
    df['asset_description'] = df['asset_description'].apply(eval)
    df2 = pd.DataFrame(df['asset_description'].values.tolist(), index=df.index)
    df.drop(columns=['asset_description'], axis=1, inplace=True)
    df = pd.merge(df, df2)

    # df['weapon_name'] = df['name'].str.replace('Souvenir ', '').astype(int) 
    ## applys may not be needed here... **
    df['weapon'] = (df['name'].apply(lambda row: row.rsplit(' |', 1)[0])
                    .apply(lambda row: row.rsplit(' ', 0)[0])
                    .replace({'Souvenir ': '', 'StatTrak™ ': '', '★ ': ''}, regex=True)
                    )
    df['skin'] = df['name'].str.extract(r'(?<=\|\s)(.*?)(?=\s\()')
    df['condition'] = df['name'].str.extract(r'(?<=\()(.*?)(?=\))')
    df['weapon_type'] = df['type'].apply(lambda row: row.rsplit(' ', 1)[1])
    df['quality'] = (df['type'].apply(lambda row: row.rsplit(' ', 1)[0])
                    .replace({'Souvenir ': '', 'StatTrak™ ': '', '★ ': ''}, regex=True)
                    )
    ## this lambda can probably be simplified... **
    df['category'] = df['name'].apply(lambda x: '★ StatTrak™' if '★' in x and 'StatTrak' in x else 'StatTrak™' if 'StatTrak' in x else '★' if '★' in x else 'Souvenir' if 'Souvenir' in x else 'Normal')

    simplified_df = df[['name', 'html_name', 'weapon', 'skin', 'condition', 'weapon_type', 'quality', 'category', 'name_color', 'sell_listings', 'sell_price', 'sell_price_text']]
    print(simplified_df)
    # print(df)
    print(simplified_df['weapon'])
    print(simplified_df['skin'])
    print(simplified_df['condition'])
    print(simplified_df['category'])
    # print(simplified_df['weapon_type'])
    
    # simplified_df.to_csv('AllWeapons3.csv', index=False, encoding='utf-8-sig')
    return df

expand_descriptions()


def weapon_stats(df):
    print(df.columns)
    print(df.head(2))
    weaponSkinDistribution_df = df.groupby(['weapon_type'])['weapon_type'].count()
    print(weaponSkinDistribution_df)

# weapon_stats(expand_descriptions())


def get_market_data(df):
    print(df)
    # print(df['html_name'].iloc[1300:2000])
    # df.to_csv('test.csv', index=False, encoding='utf-8-sig')
    allItems = df['name'].tolist()
    allItemsHTML = df['html_name'].tolist()
    priceHistoryDataframes = []
    ## move to separate function
    ## obtain price history and format columns
    for currItem, htmlItem in zip(allItems[:1], allItemsHTML[:1]): # go through all item names
        print(currItem)
        item = requests.get('https://steamcommunity.com/market/pricehistory/?appid='+ game + '&market_hash_name=' + htmlItem, cookies=cookie) # get item data
        # print(str(currRun),' out of ', str(len(allItemNames)) + ' code: ' + str(item.status_code))
        # currRun += 1
        item = item.content
        item = json.loads(item)
        item['name'] = currItem

        temp_df = pd.DataFrame.from_dict(item)
        # print(temp_df)

        priceHistoryDataframes.append(temp_df)
    # print(priceHistoryDataframes)
    priceHistory_df = pd.concat(priceHistoryDataframes).reset_index(drop=True)
    priceCol_df = pd.DataFrame(priceHistory_df['prices'].tolist(), columns=['date', 'price', 'volume'])

    priceHistory_df.drop(columns=['prices'], axis=1, inplace=True)
    priceHistory_df = pd.concat([priceHistory_df, priceCol_df], axis=1)
    priceHistory_df['date'] = priceHistory_df['date'].str[:14].astype('datetime64[ns]')
    priceHistory_df['price'] = priceHistory_df['price'].astype(float)
    priceHistory_df['volume'] = priceHistory_df['volume'].astype(int) ## potentially use df.to_numeric (test the speed difference)
    print(priceHistory_df)
    # priceHistory_df.to_csv('allpricehistory.csv', index=False, encoding='utf-8-sig')
    print(priceHistory_df['date'].dtypes)
    print(priceHistory_df['price'].dtypes)
    print(priceHistory_df['volume'].dtypes)
    # priceHistory_df.to_csv('pricehistory.csv', index=False)
        # break

        # if item:
        #     print(item.keys())
        #     print(item['price_prefix'])
        #     print(item['price_suffix'])
        #     print(item)
        #     itemPriceData = item['prices'] # is there price data?
        #     if itemPriceData == False or not itemPriceData: # if there was an issue with the request then data will return false and the for loop will just continue to the next item
        #         continue               # this could be cause the http item name was weird (eg symbol not converted to ASCII) but it will also occur if you make too many requests too fast (this is handled below)
        #     else:
        #         # initialize stuff
        #         itemPrices = [] # steam returns MEDIAN price for given time bin
        #         itemVol = []
        #         itemDate = []
        #         for currDay in itemPriceData: # pull out the actual data
        #             print(currDay)
        #             itemPrices.append(currDay[1]) # idx 1 is price
        #             itemVol.append(currDay[2]) # idx 2 is volume of items sold
        #             itemDate.append(datetime.strptime(currDay[0][0:11], '%b %d %Y')) # idx 0 is the date
                
        #         # lists are strings, convert to numbers
        #         itemPrices = list(map(float, itemPrices))
        #         itemVol = list(map(int, itemVol))
        #         print(itemPrices)
        #         print(itemVol)
        #         print(itemDate)



        # break


    ## move to separate function

# get_market_data(expand_descriptions())


def analyze_data():
    pass
    print('test')
# analyze_data()