from dataclasses import dataclass


# A wrapper for linux whois command to extract creation data
# Messy code ahead

import subprocess
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

def search(domain):
    domain_name = domain['name'] + '.' + domain['tld']
    result = None
    try:
        result = subprocess.check_output(['whois',domain_name])
    except Exception as e:
        logging.error("Exception occured")
        logging.error(str(e))
        return None
    
    if result is None:
        return result
    
    creation_date = None

    try:
        for line in result.decode().split("\n"):
            print("Line:" ,line)
            regex = "^Creation Date: .*$"
            # creation_date = re.findall(regex, line)[0].strip().split(" ")[-1].replace("Z","")
            creation_date = re.findall(regex, line)
            if len(creation_date)==0:
                continue
            creation_date = creation_date[0].strip().split(" ")[-1].replace("Z","")
            # print(creation_date)
            datetimeObj = datetime.strptime(creation_date, '%Y-%m-%dT%H:%M:%S')
            return datetimeObj
    except Exception as e:
        logging.error("Exception occured")
        logging.error(str(e))
        return None


# search({'name':'lovepuppieshome', 'tld':'co.za'})






