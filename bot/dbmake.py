import sys
import os
try:
	from .settings import BASE_DIR
except:
	from settings import BASE_DIR
sys.path.append(os.path.join(BASE_DIR))
from utils.dbconfig import dbconfig

def check():
	db = dbconfig()
	cursor = db.cursor()
	query = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA  WHERE SCHEMA_NAME = 'twitterbot'"
	cursor.execute(query)
	results = cursor.fetchall()
	db.close()
	if len(results)!=0:
		return True
	return False


def make():
	if check():
		print("Already Configured!")
		return

	print("Creating new config")

	# Create database
	db = dbconfig()
	cursor = db.cursor()
	try:
		cursor.execute("CREATE DATABASE twitterbot;")
	except Exception as e:
		print("An error occurred while trying to create db. Check if database with name 'twitterbot' already exists - if it does, delete it and try again.")
		sys.exit(0)

	print("Database 'twitterbot' created")

	# Create tables
	query = "CREATE TABLE twitterbot.scans (timestamp TEXT NOT NULL, author_username TEXT NOT NULL, author_userid TEXT NOT NULL, target_url TEXT NOT NULL, tweet_id TEXT NOT NULL, scan_results TEXT NOT NULL)"
	res = cursor.execute(query)
	print("Table 'scans' created ")
	db.close()

make()