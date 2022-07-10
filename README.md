# isitjustascam

Twitter bot developed to perform some checks on a target website and make an educated guess whether the site is scam (or fake) or real. This bot is only made to automate some basic checks and the results it generates may not be accurate sometimes. However, new checks can be added to improve the efficiency of the bot.
You can [contribute](contribute.md) new checks and features to this project.


# Setup
*Docker image coming soon.*
The bot can be setup locally by just configuring a database, and twitter API.
This setup guide assumes you have a debian-based linux machine.

## Install Requirements
```
pip install -r requirements.txt
```

## Configuring a database

- Install MySQL server
```
sudo apt install mysql-server
```
- Login as root
```
sudo mysql -u root
```
- Create a new user
```
CREATE USER 'twitterbot'@localhost IDENTIFIED BY 'password';
```

- Grant privileges
```
GRANT ALL PRIVILEGES ON *.* TO 'twitterbot'@localhost
```
- Create database and necessary tables
```
cd /bot
python dbmake.py
```


## Twitter API

You first need to create a twitter account, enable the developer mode and create a new project.

### Get API Keys

You need to then get the following credentials from your twitter developer console. Add them all into a .env file in your project's root directory. You can optionally just add these into your environment variables, whatever you prefer. 
Ignore the last variable ```TEST```. It only exists for testing purposes.
```
API_KEY=<YOUR API KEY>
API_KEY_SECRET=<YOUR API KEY SECRET>
BEARER_TOKEN=<YOUR BEARER TOKEN>
ACCESS_TOKEN=<YOUR ACCESS TOKEN>
ACCESS_TOKEN_SECRET=<YOUR ACCESS TOKEN SECRET>
USER_ID=<YOUR BOT USER ID>
BOT_USERNAME=<YOUR BOT USERNAME>
TEST=FORTEST
```

## Google Custom Search API
One of the checks requires you to have a google custom search json api key in order to perform google searches. 
You can create a custom search engine [here](https://programmablesearchengine.google.com/).
Get your API key and include it in the your environment variables (or the .env file). So your environment variables should look like this:
```
API_KEY=<YOUR API KEY>
API_KEY_SECRET=<YOUR API KEY SECRET>
BEARER_TOKEN=<YOUR BEARER TOKEN>
ACCESS_TOKEN=<YOUR ACCESS TOKEN>
ACCESS_TOKEN_SECRET=<YOUR ACCESS TOKEN SECRET>
USER_ID=<YOUR BOT USER ID>
BOT_USERNAME=<YOUR BOT USERNAME>
TEST=FORTEST
GOOGLE_SEARCH_API_KEY=<YOUR GOOGLE SEARCH API KEY>
```

## Run tests

It is always a good idea to run unit tests before deploying the bot even locally.
You can run the tests from the root directory of the project
```
python -m unittest discover -s tests
```



# Run

In-order to run the bot, you need to execute the python program ```/bot/twitterapi.py```
You can do that in the following ways:

## Method 1
Execute manually using nohup
```
nohup python bot/twitterapi.py &
```
This will execute the script in the background and will keep running even after you log off from your shell. 

## Method 2
- Create a systemd service. This is the better option.
```
cd /etc/systemd/system
```
- Create a new service
```
nano scamornot.service
```
- Paste the following
```
[Unit]
Description=Twitter bot for Scam or Not (twitter.com/isitjustascam)

[Service]
User=<your linux username>
WorkingDirectory=<absolute path of twitterapi.py>
ExecStart=python twitterapi.py

StandardOutput=file:/tmp/twitterbot-stdout
StandardError=file:/tmp/twitterbot-stderr

Restart=always

[Install]
WantedBy=multi-user.target
```
- Include the newly added service
```
sudo systemctl daemon-reload
```
- Start the service
```
sudo systemctl start scamornot.service
```
- Enable to run at startup
```
sudo systemctl enable scamornot.service
```

