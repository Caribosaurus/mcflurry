import requests
import json, os

def get_restaurants():
    url= "https://api.skipthedishes.com/customer/v1/graphql"
    headers = {
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'parameters': 'isCuisineSearch=false&isSorted=false&search=mc',
        'app-token': 'd7033722-4d2e-4263-9d67-d83854deb0fc',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    }
    data= '''{
        "operationName":"QueryRestaurantsCuisinesList",
        "variables":{
            "city":"montreal",
            "province":"QC",
            "dateTime":0,
            "isDelivery":true,
            "search":"mcdonalds",
            "sortBy":{"index":-1,"value":null},
            "language":"en","address":{}
        },
        "extensions":{"persistedQuery":{"version":1,"sha256Hash":"7b26cd706d2cb6f061afbb257debd2d8172472a5a3f94059379c78767dde5954"}}
        }'''
    
    req = requests.post(url,headers=headers,data=data)
    restaurants = []
    for restaurant in req.json()["data"]["restaurantsList"]["openRestaurants"] :
        if "mcdonalds" in restaurant['cleanUrl'] and restaurant["location"]["position"]: 
            restauItem = {
                "name": restaurant["location"]["name"],
                "url": restaurant["cleanUrl"],
                "location": restaurant["location"]["position"],
                "open": restaurant["isOpen"],
            }
            restaurants.append(restauItem)
    
    return restaurants

def get_menu(cleanUrl):
    url = "https://api-skipthedishes.skipthedishes.com/v1/restaurants/clean-url/{}?fullMenu=true&language=en".format(cleanUrl)
    headers = {
        'app-token': 'd7033722-4d2e-4263-9d67-d83854deb0fc',
    }
    
    req = requests.get(url,headers=headers)
    # skipping 0 and 1, "alergy restriction" and "popular" categories
    categories = req.json()["menu"]["menuGroups"][2:]
    items = []
    for category in categories:

        items += category["menuItems"]
    return items


restaurants_file = 'restaurants.json'
if os.path.isfile(restaurants_file):
    # print ("File exist")
    with open(restaurants_file) as f:
        restaurants = json.load(f)
else:
    # print ("File not exist")
    restaurants = get_restaurants()
    with open(restaurants_file, 'w') as json_file:
        json.dump(restaurants, json_file)

restaurants_menu = []
for restaurant in restaurants :
    menu = get_menu(restaurant["url"])
    indispo = []
    for item in menu :
        if item["available"] is not True:
            item = item["name"]
            if "Flurr" in item and "Egg" not in item:
                indispo.append(item)
    restaurant["unavailable"] = indispo 
    # if len(restaurant["unavailable"]) > 0:
    restaurants_menu.append(restaurant)

print("let restaurants={}".format(json.dumps(restaurants_menu, indent=4)))

 