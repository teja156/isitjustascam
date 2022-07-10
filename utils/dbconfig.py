import mysql.connector
import logging

logger = logging.getLogger(__name__)
  
def dbconfig():
  try:
    db = mysql.connector.connect(
      host ="localhost",
      user ="twitterbot",
      passwd ="password"
    )
    # printc("[green][+][/green] Connected to db")
    return db
  except Exception as e:
    # print("An error occurred while trying to connect to the database")
    # print(str(e))
    logger.error("Exception occured in dbconfig")
    logger.error(str(e))
    return None
  