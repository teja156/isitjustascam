import os
import unittest
import logging
from bot.settings import BASE_DIR
from utils.dbconfig import dbconfig


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

    def test_DBReadCheck(self):
        db = dbconfig()
        assert db is not None, "DB connection failed"
        cursor = db.cursor()
        query = "SELECT * FROM twitterbot.scans"
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            db.close()
        except Exception as e:
            db.close()
            logger.error("Exception occured in test_DBReadCheck")
            logger.error(str(e))
            self.fail("Unable to read from DB")
            
            
    def test_DBWriteCheck(self):
        db = dbconfig()
        assert db is not None, "DB connection failed"
        query = "INSERT INTO twitterbot.scans (timestamp,author_username,author_userid,target_url,tweet_id,scan_results) values (%s,%s,%s,%s,%s,%s)"
        val = ("timestamp","tweet_author_username","tweet_author_id","url","tweet_id","results")
        try:
            cursor = db.cursor()
            cursor.execute(query,val)
            db.commit()
            db.close()
        except Exception as e:
            db.close()
            logger.error("Exception occured in test_DBReadCheck")
            logger.error(str(e))
            self.fail("Unable to write to DB")

