from apiclient.discovery import build
import os.path
import os
from bot.settings import BASE_DIR
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

api_key = os.getenv("GOOGLE_SEARCH_API_KEY")

def search(query):
    resource = build("customsearch", 'v1', developerKey=api_key).cse()
    result = resource.list(q=query, cx='741ed1b8f60a74f53', num=10).execute()
    return result['items']


def rateControl():
    ALLOWED = 100
    today = datetime.today()
    today = today.strftime("%d")
    path = os.path.join(BASE_DIR,"tmp","googlecustomsearchquota")
    if not os.path.exists(path):
        f=open(path,"w")
        f.write(today+":"+str(0))
        f.close()
    try:
        f = open(path,"r")
        # current_used = int(f.read().strip())
        data = f.read()
        last_checked_date = int(data.strip().split(":")[0])
        current_used = int(data.strip().split(":")[-1])
        f.close()
        if last_checked_date!=today:
            # reset quota
            f=open(path,"w")
            f.write(today+":"+str(0))
            f.close()

        if (ALLOWED-current_used)>0:
            current_used+=1
            f = open(path,"w")
            f.write(str(current_used))
            f.close()

        # return how much quota is left for today
        return (ALLOWED - current_used)

    except Exception as e:
        return -1

# print((search("techraj156")))


