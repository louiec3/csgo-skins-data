import requests
import json

r = requests.get("https://steamcommunity.com/market/appfilters/730")
tags = json.loads(r.text)["facets"]["730_ItemSet"]["tags"]

winter_offensive_tag = [
	t[0] 
	for t in tags.items() 
	if t[1]["localized_name"] == "The Winter Offensive Collection"
][0]

r = requests.get(
	"https://steamcommunity.com/market/search/render/",
	params = {
		"query": "",
		"start": 1,
		"count": 100,
		"search_descriptions": 0,
		"sort_column": "price",
		"sort_dir": "asc",
		"appid": 730,
		# "category_730_ItemSet[]": f"tag_{winter_offensive_tag}",
		"category_730_ItemSet[]": "any",
		"category_730_ProPlayer[]": "any",
		"category_730_StickerCapsule[]": "any",
		"category_730_TournamentTeam[]": "any",
		"category_730_Weapon[]": "any",
        "category_730_Type[]": "tag_CSGO_Type_Pistol",
		"norender": 1
	})

data = json.loads(r.text)
print(data)
print(len(data["results"]))


    # weaponGet = requests.get(
	# "https://steamcommunity.com/market/search/render/",
	# params = {
	# 	"query": "",
	# 	"start": 1,
	# 	"count": 100,
	# 	"search_descriptions": 0,
	# 	"sort_column": "name",
	# 	"sort_dir": "asc",
	# 	"appid": game,
	# 	"category_730_ItemSet[]": "any",
	# 	"category_730_ProPlayer[]": "any",
	# 	"category_730_StickerCapsule[]": "any",
	# 	"category_730_TournamentTeam[]": "any",
	# 	"category_730_Weapon[]": "any",
    #     "category_730_Type[]": f'tag_CSGO_Type_{weapon}',
	# 	"norender": 1
	# },
    # cookies=cookie
    # )