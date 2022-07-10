import os
import unittest
import logging

from bs4 import ResultSet
import bot.twitterapi as runner
from utils.checks import Checks
import utils.checks
from bot.settings import BASE_DIR

logs_path = os.path.join(BASE_DIR,"test-logs")
if not os.path.exists(logs_path):
	os.mkdir(logs_path)

logging.basicConfig(
	handlers=[logging.FileHandler(filename=os.path.join(logs_path,'tests_log.txt'), encoding='utf-8', mode='w')],
    format='[%(asctime)s] [%(levelname)s]   %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
	force=True)
logger = logging.getLogger(__name__)

# logger.info("Tests")

class ChecksTest(unittest.TestCase):

    def test_WhoisCheck(self):
        # Test strategy:
        # - Test if the age returned is a number
        # - Test if the age returned is correct
        # - Test for website that has no whois records
        checker = Checks()
        # Format: {'url':age in days,..}
        urls = {"https://google.com":9000,"https://techraj156.com":2000,'https://pearlvine.com':2000}
        for url in urls:
            domain = utils.checks.urltodomain(url)
            result = checker.WhoisCheck(domain=domain, test=True)
            assert type(result) is dict, "result must be dict"
            age = result['age']
            assert type(age) is int,"age must be an integer"
            # checks = result['checks']
            self.assertGreater(age,urls[url],"WhoisCheck Domain age wrong")
        

    def test_GoogleCheck(self):
        # Test if search results are returned
        logger.info("TEST GoogleCheck")
        urls = {"https://fruitdeal.in":"NOK", "https://twitter.com":"OK"}
        checker = Checks()

        for url in urls:
            results = checker.GoogleCheck(url, test=True)
            assert type(results) is dict, "results must be dict"
            self.assertEqual(results['status'],urls[url],f"GoogleCheck gave wrong result for site {url}")
            self.assertGreater(len(results['results']),0,"GoogleCheck search results are empty(0)")
            for result in results['results']:
                self.assertIn('title',result,"Title missing in Search result")
                self.assertIn('snippet',result,"Snippet missing in search result")
    

    def test_DomainCheck_ServiceNames(self):
        # Check if domains containing famous service names are triggered or not
        urls = {"https://amaz0n.com":["NOK","leet"], "https://amazon.com":["OK"], "https://facebook.biz":["NOK","diff-tld"], "https://techraj156.com":["OK"], "https://amaz0n.net":["NOK","leet"], "https://abcd.ca":["OK"], "https://abc.ml":["OK"]}

        checker = Checks()
        for url in urls:
            domain = utils.checks.urltodomain(url)
            results = checker.DomainCheck_ServiceNames(domain=domain, test=True)
            # logger.info(result)

            assert type(results) is dict, "results must be must"
            if urls[url][0] == "OK":
                self.assertEqual(results['status'], "OK", f"Site {url} is legit but triggered by check")
            else:
                self.assertEqual(results['status'], "NOK", f"Site {url} is impersonating but not triggered by check")
                self.assertEqual(results['result'], urls[url][1], "Triggered unexpected condition")

    
    def test_DomainCheck_Hyphens(self):
        urls = {"https://amazon-india-shopping.biz":["NOK",2],"https://my-website.com":["OK"],"https://techraj156.com":["OK"],"https://hello-world-wassup.com":["NOK",2]}
        checker = Checks()

        for url in urls:
            domain = utils.checks.urltodomain(url)
            results = checker.DomainCheck_Hyphens(domain=domain, test=True)
            assert type(results) is dict, "results must be dict"
            self.assertEqual(results['status'], urls[url][0], f"DomainCheck_Hyphens gave wrong result for {url}")
            if urls[url][0]=='NOK':
                self.assertEqual(results['hyphen-count'],urls[url][1], f"Site {url} returned with wrong number of hypens")
            
        
    
    def test_DomainCheck_TLDS(self):
        urls = {"https://techraj156.com":["OK"], "https://mywebsite.biz":["NOK","biz"], "https://mywebsite.online":["NOK","online"], "https://mywebsite.tk":["NOK","tk"], "https://mywebsite.ml":["NOK","ml"]}
        checker = Checks()

        for url in urls:
            domain = utils.checks.urltodomain(url)
            results = checker.DomainCheck_TLDS(domain=domain, test=True)
            assert type(results) is dict, "results must be dict"
            self.assertEqual(results['status'], urls[url][0], f"DomainCheck_TLDS gave wrong result for {url}")
            if urls[url][0] == 'NOK':
                self.assertEqual(results['tld'],urls[url][1],f"Wrong tld match for site {url}")
        
    
    def test_BadGrammarCheck(self):
        urls = {"https://www.cnbc.com":"OK", "https://teja156.github.io/sample-githubpage-for-grammartest":"NOK", "https://fruitdeal.in":"FAIL"}
        checker = Checks()

        for url in urls:
            results = checker.BadGrammarCheck(URL=url, test=True)
            assert type(results) is dict, "results must be dictionary"
            self.assertEqual(results['status'], urls[url], "Grammar check gave wrong results")

    def test_ContactPageCheck(self):
        urls = {"https://techraj156.com":"OK","https://fruitdeal.in":"FAIL","http://mylocalsite.online/":"FAIL"}
        checker = Checks()

        for url in urls:
            domain = utils.checks.urltodomain(url)
            results = checker.ContactPageCheck(domain=domain, test=True)
            assert type(results) is dict, "results must be dict"
            self.assertEqual(results['status'], urls[url], f"ContactPageCheck gave wrong result for site {url}")


    
    
        
    
        
    



