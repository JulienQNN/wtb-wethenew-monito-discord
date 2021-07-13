from os import link
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent
from fp.fp import FreeProxy
from urllib.parse import urlunsplit, urlencode
import requests as rq
import time
import json
import logging
import dotenv
import urllib3
from datetime import datetime

"""
logs
"""
logging.basicConfig(filename='MonitoLog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)
"""
configurations
"""
hardware_type = [HardwareType.MOBILE__PHONE]
software_names = [SoftwareName.CHROME.value]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()
proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)
"""
stored values
"""
INSTOCK = []
"""
scraper
"""
def scrape_site(url, headers, proxy):
    items = []
    """
    Makes request to site
    """
    s = rq.Session()
    page = 0
    while True:
        html = s.get(url, headers=headers, proxies=proxy, verify=False, timeout=20)
        output = json.loads(html.text)
        if output == []:
            break
        elif page == 1:
            break
        else:
            """
            Stores particular details in array
            """
            for product in output:
                productitem = {
                    'name': product['name'], 
                    'image': product['image'], 
                    'sizes': product['sizes']}
                items.append(productitem)
            """
            #force to break after scraping every products
            """
            page += 1 
             
    logging.info(msg='Successfully scraped site')
    s.close()
    return items

def checker(item):
    """
    Determines whether the product status has changed
    """
    return item in INSTOCK

def discord_webhook(name, url, thumbnail, sizes):
    """
    Second way to make embeds looks
    """
    
    """
    namereplace = name.replace(" ","%20")
    FinalLinkParentheseSolve = namereplace.replace(")","%29")
    link ="[PROPOSEZ](https://wethenew.typeform.com/to/YHVxNu?sneaker="
 
    linkfinal = ''f'{link + FinalLinkParentheseSolve})'
    
    fieldsSizes = []

    fieldsSizes.append({"name":"WeTheNew", "value":"Propose ta paire \u200b ⬇", "inline": False})
    for size in sizes:
        fieldsSizes.append({"name":"\u200b", "value":linkfinal + "\n" + size, "inline": True}),
    
   """  
    
    namereplace = name.replace(" ","%20")
    FinalLinkParentheseSolve = namereplace.replace(")","%29")
    link ="[PROPOSEZ](https://wethenew.typeform.com/to/YHVxNu?sneaker="
 
    linkfinal = ''f'{link + FinalLinkParentheseSolve})' 
    
    ListeSizes = []
    fieldsSizes = []
    
    fieldsSizes.append({"name":"WeTheNew", "value":"Propose ta paire \u200b ⬇", "inline": False})
    
    for size in sizes:
        ListeSizes.append(linkfinal + " \u200b " + size),
        
    listesizes= ' \u200b'.join(sizes)
    last = '\n'.join(ListeSizes)   
    fieldsSizes.append({"name":"\u200b", "value":last, "inline": False}),
    namesize = name + " \u200b "+"·"+ " \u200b "+ listesizes + " \u200b " 
         
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "author": {
            "name": "Izi Cookz", 
            "url": "https://dashboard.izicookz.com/",
            "icon_url": CONFIG['AVATAR_URL'],
            },
            "title": namesize,
            "thumbnail": {"url": thumbnail},
            "color": int(CONFIG['COLOUR']),
            "fields": fieldsSizes,
            "url": "https://wtb.wethenew.com/",
            "footer": {"text": "Made by JLM for Izi Cookz","icon_url": "https://media1.tenor.com/images/bcebfc84143c63f127c7fd80826f01bf/tenor.gif?itemid=22297787"},
            "timestamp": str(datetime.utcnow()),
        }]
    }
    """
    Wait 5 secondes betweens webhook to avoid spam
    """
    time.sleep(5)
    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return list(set(mylist))


def comparitor(product, start):
    product_item = [product['name'], product['image'], product['sizes']]
    """
    Collect all available sizes
    """
    available_sizes = []
    for size in product['sizes']:
        available_sizes.append(size)
    if product_item:
        if not checker(product_item):
            # If product is available but not stored - sends notification and stores
            
            INSTOCK.append(product_item)

            if start == 0:
                discord_webhook(
                    name=product['name'],
                    url="https://wtb.wethenew.com/",
                    thumbnail=product['image'],
                    sizes=available_sizes
                )
                logging.info(msg='Successfully sent Discord notification')

    else:
        if checker(product_item):
            # If product is not available but stored - removes from store
            INSTOCK.remove(product_item)


def monitor():
    """
    Initiates the monitor
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    """
    Tests webhook URL
    """  
    # test_webhook()
    """
    start = 0 will notif discord at start of every products
    """
    start = 1
    """
    Initialising proxy and headers
    """
    proxy_no = 0
    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": proxyObject.get()} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}

    # Collecting all keywords (if any)
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            # Makes request to site and stores products 
            items = scrape_site(CONFIG['URL'], proxy, headers)
            for p in items:
                if keywords == "":
                    # If no keywords set, checks whether item status has changed
                    comparitor(p, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                            comparitor(p, start)

            # Allows changes to be notified
            start = 0

            # User set delay
            time.sleep(float(CONFIG['DELAY']))

        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)

            # Rotates headers
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            
            if CONFIG['PROXY'] == "":
                # If no optional proxy set, rotates free proxy
                proxy = {"http": proxyObject.get()}

            else:
                # If optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}
                
if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()