import os
import unittest
import logging
import bot.twitterapi as runner
import utils.checks as checker
from bot.settings import BASE_DIR
from bot.tweettest import retrieveTweet
from dotenv import load_dotenv

load_dotenv()

# What to test
# - If it was able to parse the URL from a tweet 
# - If the resolve from t.co to target URL is happening
# - Connectivity check of the target URL 
# - All the checks for a URL
# - Analyze the results and prepare a tweet text 


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


class GeneralTests(unittest.TestCase):
    def test_parseURL(self):
        tweet = {'data': [{'author_id': '1266049140624027648', 'id': '1544527288049750017', 'text': '@isitjustascam TWEET TEST PARSE URL https://t.co/cIlpTMSBPC'}], 'includes': {'users': [{'id': '1266049140624027648', 'name': 'WICK', 'username': 'WICK67644329'}]}, 'meta': {'result_count': 1, 'newest_id': '1544527288049750017', 'oldest_id': '1544527288049750017'}}
        expected_url = "https://t.co/cIlpTMSBPC"
        result_url = runner.parseTweets(tweets=tweet,test=True)
        self.assertEqual(result_url, expected_url, "Retrieve URL from the tweet")
    
    def test_resolveURL(self):
        url = "https://t.co/cIlpTMSBPC"
        result_url = runner.resolveTwitterURL(url)
        expected_url = "https://www.techraj156.com/"
        self.assertEqual(result_url, expected_url, "Resolve t.co to target URL")
    
    def test_connectivityCheck_yes(self):
        url = "https://google.com"
        self.assertTrue(runner.checkConnectivity(url),"Connectivity check to target URL success")
    
    def test_connectivityCheck_no(self):
        result = runner.checkConnectivity("http://fruitdeal.in/")[0]
        self.assertFalse(result,"Connectivity check to target URL failure")


    def test_analyzeCreateResponse_real(self):
        url = "https://techraj156.com"
        checks = {'DomainCheck_ServiceNames': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 9, 'description': set()}, 'DomainCheck_Hyphens': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'DomainCheck_TLDS': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'GoogleCheck': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 20, 'description': set()}, 'BadGrammarCheck': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'WhoisCheck': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 10, 'description': set()}, 'ContactPageCheck': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}}
        result = runner.analyzeAndPostResponse(checks=checks,sus_score=0,url=url,tweet={},test=True)
        formatted_url = url.replace(".","[.]")
        expected_tweet_text = f"Scan results for {formatted_url}\nSite looks SAFE. \nBut remember - if you feel something is too good to be true, it is probably just a scam."
        self.assertEqual(result['tweet_text'],expected_tweet_text,"Prepare response based on check results - real")
    

    def test_analyzeCreateResponse_sus(self):
        url = "https://samosakennels.co.za/"
        checks = {'DomainCheck_ServiceNames': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 9, 'description': set()}, 'DomainCheck_Hyphens': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'DomainCheck_TLDS': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'GoogleCheck': {'status': 'NOK', 'SUS_SCORE': 6, 'MAX_SUS_SCORE': 6, 'description': {'Google search results are sus'}}, 'BadGrammarCheck': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'WhoisCheck': {'status': 'NOK', 'SUS_SCORE': 10, 'MAX_SUS_SCORE': 10, 'description': {'Site is very young (8 days old)'}}, 'ContactPageCheck': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}}
        result = runner.analyzeAndPostResponse(checks=checks,sus_score=16,url=url,tweet={},test=True)
        logger.info(f"Tweet text: {result['tweet_text']}")
        self.assertIn("SUSPICIOUS",result['tweet_text'],"Prepare response based on check results - sus")

    
    def test_analyzeCreateResponse_scam(self):
        url = "https://samosakennels.co.za/"
        checks = {'DomainCheck_ServiceNames': {'status': 'NOK', 'SUS_SCORE': 5, 'MAX_SUS_SCORE': 9, 'description': set()}, 'DomainCheck_Hyphens': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'DomainCheck_TLDS': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}, 'GoogleCheck': {'status': 'NOK', 'SUS_SCORE': 6, 'MAX_SUS_SCORE': 6, 'description': {'Google search results are sus'}}, 'BadGrammarCheck': {'status': 'NOK', 'SUS_SCORE': 4, 'MAX_SUS_SCORE': 2, 'description': set()}, 'WhoisCheck': {'status': 'NOK', 'SUS_SCORE': 10, 'MAX_SUS_SCORE': 10, 'description': {'Site is very young (8 days old)'}}, 'ContactPageCheck': {'status': 'OK', 'SUS_SCORE': 0, 'MAX_SUS_SCORE': 2, 'description': set()}}
        result = runner.analyzeAndPostResponse(checks=checks,sus_score=25,url=url,tweet={},test=True)
        logger.info(f"Tweet text: {result['tweet_text']}")
        self.assertIn("SCAM",result['tweet_text'],"Prepare response based on check results - scam")

    def test_twitterApiTest(self):
        tweet_id = "1544527288049750017"
        result = retrieveTweet(tweet_id=tweet_id)
        assert type(result) is dict, "result must be dict"
        self.assertIn("TWEET TEST PARSE URL", result['text'], "Tweet doesn't contain expected text")

    
    def test_envCheck(self):
        test_env = os.getenv("TEST")
        self.assertEqual(test_env,"FORTEST","Environment variables not accessible")

    def test_WhitelistSites(self):
        urls = {"https://google.com":"OK", "https://amazon.com":"OK","https://techraj156.com":"NOK","https://blogger.com":"OK"}
        for url in urls:
            results = runner.checkWhitelist(url=url, test=True)
            assert type(results) is dict, "results must be dict"
            self.assertEqual(results['status'],urls[url])





        

    


        



