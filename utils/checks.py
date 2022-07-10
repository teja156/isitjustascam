import csv
import os
from ctypes.wintypes import CHAR
from email import header
from xml import dom
import utils.googlecustomsearch
import utils.grammarcheck
import requests
from bs4 import BeautifulSoup
import whois
import datetime
import logging
# from base_logger import logger
import tldextract
import utils.linuxwhois
from bot.settings import BASE_DIR


logger = logging.getLogger(__name__)

# print(CHECKS)

def urltodomain(url):
    extracted = tldextract.extract(url)
    return {'subdomain':extracted.subdomain,'name':extracted.domain, 'tld':extracted.suffix}


def performChecks(url,test=False):
    domain = urltodomain(url)
    # print("Domain: ",domain, type(domain))
    logger.info(f"Performing checks for {url}")
    # print(f"Performing checks for {url}")

    logger.info(f"Domain {str(domain)}")

    # Perform Checks
    checker = Checks()
    checker.WhoisCheck(domain)
    checker.GoogleCheck(url)
    checker.DomainCheck_ServiceNames(domain)
    checker.DomainCheck_Hyphens(domain)
    checker.DomainCheck_TLDS(domain)
    checker.BadGrammarCheck(url)
    checker.ContactPageCheck(domain)

    # print("Final SUS SCORE: ",checker.SUS_SCORE)
    logger.info("ALL CHECKS DONE")
    logger.info(f"CHECKS status: {str(checker.CHECKS)}")
    logger.info(f"FINAL SUS SCORE: {checker.SUS_SCORE}")

    # logger.info(f"Final SUS SCORE: {checker.SUS_SCORE}")

    return [checker.CHECKS, checker.SUS_SCORE]



class Checks():
    def __init__(self):
        logger.info("Instantiating Object checker")
        self.CHARS_TO_DIGITS = {'a':4, 'b': 6, 'e': 3, 'f': 7, 'g': 9, 'h': 4, 'i': 1, 'l': 1, 'o':0, 's': 5, 't': 7}
        self.SUS_SCORE = 0
        self.CHECKS = {
        'DomainCheck_ServiceNames': {'status': 'OK', 'SUS_SCORE':0, 'MAX_SUS_SCORE':9, 'description':set()},
        'DomainCheck_Hyphens': {'status':'OK', 'SUS_SCORE':0, 'MAX_SUS_SCORE':2,'description':set()},
        'DomainCheck_TLDS': {'status':'OK', 'SUS_SCORE':0, 'MAX_SUS_SCORE':2,'description':set()},
        'GoogleCheck': {'status':'OK', 'SUS_SCORE':0, 'MAX_SUS_SCORE':20,'description':set()},
        'BadGrammarCheck': {'status':'OK', 'SUS_SCORE':0, 'MAX_SUS_SCORE':2,'description':set()},
        'WhoisCheck': {'status':'OK', 'SUS_SCORE':0, 'MAX_SUS_SCORE':10,'description':set()},
        'ContactPageCheck': {'status':'OK', 'SUS_SCORE':0, 'MAX_SUS_SCORE':2,'description':set()},
        }
    

    def __del__(self):
        logger.info("Destroying Object checker")
        self.CSV_FILE = ''
        self.CHARS_TO_DIGITS = {}
        self.SUS_SCORE = 0
        self.CHECKS = {}
    

    def DomainCheck_ServiceNames(self, domain, test=False):
        TEST = {'status':'OK'}
        local_sus_score = 0
        logger.info("CHECK DomainCheck_ServiceNames")
        path = os.path.join(BASE_DIR,"utils","top500Domains.csv")
        csvreader = []
        with open(path, newline='') as f:
            reader = csv.reader(f)
            csvreader = list(reader)
            csvreader = csvreader[1:]

        for row in csvreader:
            d = row[1]
            # First get the actual domain name without subdomains
            # famousdomain = {'name':d.split('.')[-2], 'tld':d.split('.')[-1]}

            extracted = tldextract.extract(d)
            famousdomain = {'name':extracted.domain, 'tld':extracted.suffix}
            famousdomain_name = famousdomain['name']
            domain_name = domain['name']

            if len(famousdomain_name)<=4:
                continue

            # If the site is indeed a famous domain
            if domain_name.lower() == famousdomain_name.lower() and domain['tld'].lower() == famousdomain['tld'].lower():
                if test:
                    return TEST
                self.CHECKS['DomainCheck_ServiceNames']['status'] = 'OK'
                self.CHECKS['DomainCheck_ServiceNames']['description'] = set()
                self.CHECKS['DomainCheck_ServiceNames']['SUS_SCORE']=0
                break

            # Name is same but tld is different
            if domain['name'].lower() == famousdomain['name'].lower() and domain['tld'].lower()!=famousdomain['tld'].lower():
                logger.info(f"Found tld difference {famousdomain_name}: ")
                if test:
                    TEST['status'] = 'NOK'
                    TEST['result'] = 'diff-tld'
                    return TEST
                # self.SUS_SCORE+= 1
                local_sus_score+=2
                logger.info("SUS_SCORE+=1")
                self.CHECKS['DomainCheck_ServiceNames']['status'] = 'NOK'
                self.CHECKS['DomainCheck_ServiceNames']['description'].add(f'Appears to impersonate a famous site ({famousdomain_name}) with a diff tld.')
                self.CHECKS['DomainCheck_ServiceNames']['SUS_SCORE']+=local_sus_score
                

            # Check for leet
            tmp=domain['name'].lower()
            for i in self.CHARS_TO_DIGITS:
                if str(self.CHARS_TO_DIGITS[i]) in tmp:
                    tmp = tmp.replace(str(self.CHARS_TO_DIGITS[i]), i)
            
            # print(tmp)
            
            if tmp!=domain['name'].lower() and famousdomain['name'].lower() in tmp:
                logger.info(f"Found leet {tmp} {famousdomain_name}")
                if test:
                    TEST['status'] = 'NOK'
                    TEST['result'] = 'leet'
                    return TEST
                # self.SUS_SCORE+=2
                local_sus_score+=5
                logger.info("SUS_SCORE+=2")
                self.CHECKS['DomainCheck_ServiceNames']['status'] = 'NOK'
                self.CHECKS['DomainCheck_ServiceNames']['description'].add(f'Appears to impersonate a famous website ({famousdomain_name}) with a diff tld.')
                self.CHECKS['DomainCheck_ServiceNames']['SUS_SCORE']+=local_sus_score
            
        
        if test:
            return TEST
        
        self.SUS_SCORE+=local_sus_score


    def DomainCheck_Hyphens(self, domain, test=False):
        TEST = {'status':'OK'}
        local_sus_score = 0
        logger.info("CHECK DomainCheck_Hyphens")
        hyphen_count = domain['name'].count('-')
        domain_name = domain['name']
        if hyphen_count>1:
            logger.info(f"Excessive hypens found {domain_name}")
            # self.SUS_SCORE+=1
            local_sus_score+=2
            logger.info("SUS_SCORE+=2")
            self.CHECKS['DomainCheck_Hyphens']['status'] = 'NOK'
            self.CHECKS['DomainCheck_Hyphens']['description'].add(f'Excessive hyphens')
            self.CHECKS['DomainCheck_Hyphens']['SUS_SCORE']+=local_sus_score
            if test:
                TEST['status'] = 'NOK'
                TEST['hyphen-count'] = hyphen_count
        
        if test:
            return TEST

        self.SUS_SCORE+=local_sus_score


    def DomainCheck_TLDS(self, domain, test=False):
        TEST = {'status':'OK'}
        local_sus_score = 0
        logger.info("CHECK DomainCheck_TLDS")
        path = os.path.join(BASE_DIR,"utils","lesstrustedtlds.txt")
        with open(path,'r') as f:
            for d in f.readlines():
                if d=="" or d==" ":
                    continue
                if domain['tld'] == d.strip():
                    domain_tld = domain['tld']
                    logger.info(f"Found less trusted TLD {domain['name']} .{domain_tld}")
                    
                    # self.SUS_SCORE+=2
                    local_sus_score+=2
                    logger.info("SUS_SCORE+=2")
                    self.CHECKS['DomainCheck_TLDS']['status'] = 'NOK'
                    self.CHECKS['DomainCheck_TLDS']['description'].add(f'Less trusted TLD ({domain_tld})')
                    self.CHECKS['DomainCheck_TLDS']['SUS_SCORE']+=local_sus_score
                    if test:
                        TEST['status'] = 'NOK'
                        TEST['tld'] = domain['tld']
                    break
        
        if test:
            return TEST
        
        self.SUS_SCORE+=local_sus_score


    def GoogleCheck(self, URL, test=False):
        TEST = {'status':'OK'}
        local_sus_score = 0
        logger.info("CHECK GoogleCheck")

        if utils.googlecustomsearch.rateControl() <= 0:
            logger.error("Allowed quota for googlecustomsearch is over, so not performing this check")
            self.CHECKS['GoogleCheck']['status'] = 'FAIL'
            if test:
                TEST['status'] = 'FAIL'
                return TEST
            return

        results = None
        try:
            results = utils.googlecustomsearch.search(URL)
        except Exception as e:
            logger.error("Exception occured")
            logger.error(str(e))
            self.CHECKS['GoogleCheck']['status'] = 'FAIL'
            if test:
                TEST['status'] = 'FAIL'
                return TEST
            return
        
        
        sus_words = ['fraud','complaint','scam','real or fake','review','reviews','consumer','fake','customer']


        if len(results)>0:
            self.CHECKS['GoogleCheck']['MAX_SUS_SCORE'] = 2*len(results)
        else:
            self.CHECKS['GoogleCheck']['status'] = 'FAIL'
            logging.info("No search results returned by the API, skipping check")
            if test:
                TEST['status'] = 'FAIL'
                return TEST
            return


        for result in results:
            title = ''
            snippet = ''
            url = ''
            if 'title' in result:
                title = result['title'].lower()
            if 'snippet' in result:
                snippet = result['snippet'].lower()
            if 'displayLink' in result:
                url = result['displayLink'].lower()
            
            extracted1 = None
            search_domain = {'name':'', 'tld':''}
            try:
                extracted1 = tldextract.extract(url)
                search_domain = {'name':extracted1.domain, 'tld':extracted1.suffix}
            except Exception as e:
                logging.info("Exception occured")
                logging.info(str(e))
            
            extracted2 = tldextract.extract(URL)
            domain = {'name':extracted2.domain, 'tld':extracted2.suffix}

            logger.info(f"Search Results for {URL}")
            logger.info(f"Title: {title}")
            logger.info(f"Snippet: {snippet}")
            logger.info(f"URL: {url}")

            # print(title)
            # print(snippet)
            # print(url)

            for sus_word in sus_words:
                if sus_word in title or sus_word in snippet:
                    if search_domain['name'] == domain['name'] and search_domain['tld'] == domain['tld']:
                        continue
                    logger.info(f"Found sus word {sus_word} in search result")
                    # self.SUS_SCORE+=1
                    local_sus_score+=2
                    logger.info("SUS_SCORE+=2")
                    # print(self.CHECKS)s
                    self.CHECKS['GoogleCheck']['status'] = 'NOK'
                    self.CHECKS['GoogleCheck']['description'].add('Google search results are sus')
                    if test:
                        TEST['status'] = 'NOK'
                    break
        
        self.CHECKS['GoogleCheck']['SUS_SCORE']+=local_sus_score
        self.SUS_SCORE+=local_sus_score

        if test:
            TEST['results'] = results
            return TEST


    def BadGrammarCheck(self, URL, test=False):
        TEST = {'status':'OK'}
        local_sus_score = 0
        logger.info("CHECK BadGrammarCheck")
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        r = None

        try:
            r = requests.get(URL,headers=headers, timeout=10)
        except Exception as e:
            logger.error("Exception occured")
            logger.error(str(e))
            self.CHECKS['BadGrammarCheck']['status'] = 'FAIL'
            TEST['status']='FAIL'
            if test:
                return TEST
            return

        if r.status_code!=200:
            logger.error(f"Couldn't connect to site, response code: {r.status_code}")
            self.CHECKS['BadGrammarCheck']['status'] = 'FAIL'
            TEST['status']='FAIL'
            if test:
                return TEST
            return
        
        try:
            soup = BeautifulSoup(r.text,'html.parser')
            ok = 0
            notok = 0
            title_text = soup.find('title').get_text()
            if title_text.strip().count(" ")>2: # more than 3 words
                # logger.info(f"Checking grammar for '{title_text}'")
                if utils.grammarcheck.check(title_text):
                    # print(f"{title_text}: Grammar ok\n\n")
                    logger.info(f"Grammar OK for '{title_text}'")
                    ok+=1
                else:
                    # print(f"{title_text}: Grammar not ok\n\n")
                    logger.info(f"Grammar NOT OK for '{title_text}'")
                    notok+=1

            para_texts = []

            for i in soup.find_all('p'):
                para = i.get_text()
                if para.count(" ")>2:
                    # logger.info(f"Checking grammar for '{para}'")
                    if utils.grammarcheck.check(para):
                        # print(f"{para}: Grammar ok\n\n")
                        logger.info(f"Grammar OK for '{para}'")
                        ok+=1
                    else:
                        # print(f"{para}: Grammar not ok\n\n")
                        logger.info(f"Grammar NOT OK for '{para}'")
                        notok+=1
            
            logger.info(f"OK: {ok}")
            logger.info(f"NOTOK: {notok}")

            if (ok+notok)!=0:
                positive = ok*100//(ok+notok)
                negative = notok*100//(ok+notok)

                # print("Grammer ok %: ", positive)
                # print("Grammer not ok %: ", negative)

                logger.info(f"OK%: {positive}")
                logger.info(f"NOTOK%: {negative}")

                if negative > 50 and negative <= 75:
                    # self.SUS_SCORE+=1
                    local_sus_score+=1
                    logger.info("SUS_SCORE+=1")
                    self.CHECKS['BadGrammarCheck']['status'] = 'NOK'
                    self.CHECKS['BadGrammarCheck']['description'].add('Grammar on site looks bad')
                    self.CHECKS['BadGrammarCheck']['SUS_SCORE']+=local_sus_score
                    if test:
                        TEST['status'] = 'NOK'
                        TEST['sus_score'] = local_sus_score
                
                if negative > 75:
                    # self.SUS_SCORE+=2
                    local_sus_score+=2
                    logger.info("SUS_SCORE+=2")
                    self.CHECKS['BadGrammarCheck']['status'] = 'NOK'
                    self.CHECKS['BadGrammarCheck']['description'].add('Grammar on site looks very bad')
                    self.CHECKS['BadGrammarCheck']['SUS_SCORE']+=local_sus_score
                    if test:
                        TEST['status'] = 'NOK'
                        TEST['sus_score'] = local_sus_score
            
            else:
                # print("Couldn't perform grammar check")
                logger.info("Couldn't perform grammar check on the content")
                self.CHECKS['BadGrammarCheck']['status'] = 'FAIL'
                if test:
                    TEST['status'] = 'FAIL'
        except Exception as e:
            logger.error("Exception occured")
            logger.error(str(e))
            self.CHECKS['BadGrammarCheck']['status'] = 'FAIL'
            if test:
                TEST['status'] = 'FAIL'
        
        self.SUS_SCORE+=local_sus_score
        if test:
            logger.info(f"TEST: {TEST}")
            return TEST


    def WhoisCheck(self, domain, test=False):
        TEST = {'status':'OK'}
        local_sus_score = 0
        logger.info("CHECK WhoisCheck")
        # print("Doing whoischeck")
        w = None
        try:
            w = whois.whois(domain['name']+'.'+domain['tld'])
        except Exception as e:
            logger.error("Exception occured")
            logger.error(str(e))
            self.CHECKS['WhoisCheck']['status'] = 'FAIL'
            if test:
                TEST['status'] = 'FAIL'
                return TEST
            return

        now = datetime.datetime.now()
        now = now.replace(tzinfo=None)
        creation_date = w['creation_date']
        logger.info(f"Creation date: {creation_date}")

        if creation_date is None:
            logging.info("Not able to extract creation date from official whois query")
            logging.info("Using Linux 'whois' command")
            creation_date = utils.linuxwhois.search(domain)
            if creation_date is None:
                logging.error("Couldn't retrieve creation date from Linux 'whois'")
                logging.error("Failed to perform Whoischeck")
                self.CHECKS['WhoisCheck']['status'] = 'FAIL'
                if test:
                    TEST['status'] = 'FAIL'
                    return TEST
                return


        if isinstance(creation_date, list):
            creation_date = creation_date[-1]

        # creation date could be a datetime object or a timestamp string
        if isinstance(creation_date,datetime.datetime):
            logger.info("creation_date is datetime object")
            creation_date = creation_date.replace(tzinfo=None)
        else:
            # create datetime object from timestamp string
            try:
                logger.info("creation_date is timestamp string")
                creation_date = creation_date.strip().replace("Z","")
                creation_date = datetime.datetime.strptime(creation_date,"%Y-%m-%dT%H:%M:%S")
                logger.info(f"Converted to datetime object {creation_date}")
            except Exception as e:
                logger.error("EXCEPTION OCCURED")
                logger.error("Exception occured while trying to convert timestamp string to datetime object")
                logger.error(str(e))
                if test:
                    TEST['status']= 'FAIL'
                    return TEST
        
        age = now - creation_date
        age = int(age.total_seconds()/86400)
        # print(age)
        logger.info(f"Age: {age}")
        if test:
            TEST['age'] = age

        if age<=30:
            # self.SUS_SCORE+=5
            logging.info("Age<=30")
            local_sus_score+=10
            logger.info("SUS_SCORE+=10")
            self.CHECKS['WhoisCheck']['status'] = 'NOK'
            self.CHECKS['WhoisCheck']['description'].add(f'Site is very young ({age} days old)')
            self.CHECKS['WhoisCheck']['SUS_SCORE']+=local_sus_score
            if test:
                TEST['status'] = "NOK"
        
        elif age>30 and age<=90:
            # self.SUS_SCORE+=3
            logging.info("Age<30 and <=90")
            local_sus_score+=5
            logger.info("SUS_SCORE+=3")
            self.CHECKS['WhoisCheck']['status'] = 'NOK'
            self.CHECKS['WhoisCheck']['description'].add(f'Site is young ({age} days old)')
            self.CHECKS['WhoisCheck']['SUS_SCORE']+=local_sus_score
            if test:
                TEST['status'] = "NOK"
        
        elif age>90 and age<=180:
            # self.SUS_SCORE+=2
            logging.info("Age>90 and <=180")
            local_sus_score+=3
            logger.info("SUS_SCORE+=2")
            self.CHECKS['WhoisCheck']['status'] = 'NOK'
            self.CHECKS['WhoisCheck']['description'].add(f'Site is young ({age} days old)')
            self.CHECKS['WhoisCheck']['SUS_SCORE']+=local_sus_score
            if test:
                TEST['status'] = "NOK"


        elif age>180 and age<=360:
            # self.SUS_SCORE+=1
            logging.info("Age>180 and <=360")
            local_sus_score+=1
            logger.info("SUS_SCORE+=1")
            self.CHECKS['WhoisCheck']['status'] = 'NOK'
            self.CHECKS['WhoisCheck']['description'].add(f'Site is young ({age} days old)')
            self.CHECKS['WhoisCheck']['SUS_SCORE']+=local_sus_score
            if test:
                TEST['status'] = "NOK"
        
        # print("after whoischeck: ",self.CHECKS)

        self.SUS_SCORE+=local_sus_score

        if test:
            return TEST
    


    def ContactPageCheck(self, domain, test=False):
        TEST = {'status':'OK'}
        local_sus_score = 0
        logger.info("CHECK ContactPageCheck")
        url = "https://"+domain['name'] + '.' + domain['tld']
        contact_pages = ["contact","contact-us","get-in-touch","support","about/contact","about/contact-us","ticket","support/ticket"]
        exists = False
        for i in contact_pages:
            logger.info(f"Trying {url}/{i}")
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
            r = None
            try:
                r = requests.get(url+"/" + i, headers=headers, timeout=10)
            except Exception as e:
                logger.error("Exception occured")
                logger.error(str(e))
                self.CHECKS['ContactPageCheck']['status'] = 'FAIL'
                if test:
                    TEST['status'] = 'FAIL'
                    return TEST
                return

            if r.status_code == 200:
                logger.info("Status code is 200")
                words = ["contact","email","phone","landline","location","map","address"]
                for word in words:
                    if word in r.text.lower():
                        logger.info(f"Found {word} in page")
                        exists = True
                        break
            if exists:
                break
        
        if not exists:
            logger.info("Page doesn't exist")
            # self.SUS_SCORE+=2
            local_sus_score+=2
            logger.info("SUS_SCORE+=2")
            self.CHECKS['ContactPageCheck']['status'] = 'NOK'
            self.CHECKS['ContactPageCheck']['description'].add(f'Contact page not found')
            self.CHECKS['ContactPageCheck']['SUS_SCORE']+=local_sus_score

            if test:
                TEST['status'] = 'NOK'
        
        # print(self.SUS_SCORE)
        if test:
            return TEST
        self.SUS_SCORE+=local_sus_score


# DomainCheck_ServiceNames({'name':'amaz0n','tld':'net'})
# DomainCheck_Hyphens({'name':'amazon-india-shopping','tld':'biz'})
# DomainCheck_TLDS({'name':'amazon-india-shopping','tld':'biz'})
# GoogleCheck({'name':'fruitdeal','tld':'in'})
# BadGrammarCheck("https://techraj156.com")
# WhoisCheck({'name':'techraj156','tld':'com'})

# ContactPageCheck("https://techraj156.com")
