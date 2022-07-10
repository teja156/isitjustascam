# Contribute
Thanks for taking a moment to think about contributing to this project.
Together we can -
- Add new checks to improve the efficiency of the bot
- Bring new features
- Fix unexpected bugs
- Altogether, help eradicate internet scams

## Basic Terminology
#### SUS_SCORE
SUS_SCORE is a value that we maintain to keep a note of the actual result of a particular scan.  Each check has its own SUS_SCORE. The scores of all the checks are added after all the checks are done to finally come up with a decision. 
#### MAX_SUS_SCORE
MAX_SUS_SCORE is the total SUS_SCORE that your check can return. It is used to create a percentage (%) value when deciding the output of a site scan. Each check has its own MAX_SUS_SCORE. 

You can decide upon the SUS_SCORE and MAX_SUS_SCORE based on how much you think your new check should implement the overall output of the scan.

#### Calculating the percentage from SUS_SCORE and MAX_SUS_SCORE
After all checks are done, we calculate a percentage in-order to come up with a decision for the scan. We take the total_sus_score and the total_max_sus_score from all the checks and do this: 
```
sus_percentage = math.ceil((total_sus_score*100)/(total_max_sus_score))
```
Based on the achieved sus_percentage we make a decision.

## Adding new check
You can add new checks to the bot by following the below steps - 
### Name your check
Come up with a 'name' for your new check. The name must obviously not have any spaces as it will be used to name the corresponding function in the code. You can use underscores instead of spaces. Short names are appreciated to make it more readable for others.
### Define your check
Define your check in the ***CHECKS*** dictionary inside the Checks() class.
Follow this pattern:
```
'CHECK_NAME': {'status':'OK', SUS_SCORE: 0, 'MAX_SUS_SCORE': <max sus score of your check>, 'description': set()}
```


### Write your check
You can add your check as a function in *utils/checks.py* 
Take necessary inputs to your check as function parameters. Include an additional parameter called 'test' which defaults to False. This will be used later when writing tests for your check.
After performing your check, add your check results into the 'CHECKS' dictionary. 
The CHECKS dictionary has 4 attributes.
status: 
- 'OK' if your check passed for the target url 
-  'NOK' if your check failed for the target url
- 'FAIL' if your check failed to execute

SUS_SCORE
- Increment the sus_score accordingly based on different conditions in your check

MAX_SUS_SCORE
- Give your check a MAX_SUS_SCORE depending on how much you think your check should contribute to the overall output of the scan

description
- Add a description for why your check failed for the target url (can be multiple reasons)

Example:
```
def My_NewCheck(self, url, test=False):
	local_sus_score = 0 # used to maintain the sus_score that is local to your check only
	TEST = {'status':'OK'} # Used for tests
	
	# Write your code here
	...
	...
	...
	...
	# Add check results
	self.CHECKS['DomainCheck_ServiceNames']['status'] = 'NOK'
	self.CHECKS['DomainCheck_ServiceNames']['description'].add(f'some reason')
	self.CHECKS['DomainCheck_ServiceNames']['SUS_SCORE']+=local_sus_score
	...
	...
	# Add your local_sus_score to the global SUS_SCORE
	self.SUS_SCORE+=local_sus_score
	
```

Now add your check's function call in the performChecks() function like this,
```
checker.My_NewCheck(url)
```
## Write tests for your check
It is very ESSENTIAL that you test your check properly. Therefore you need to create a new unit test for your newly written check.
Add a test case in ```tests/tests_checks.py```
Your testcase function should be in this format: ```test_CheckName```
The concept is pretty straight forward - 
- Call your check with a test input
- Store the result obtained
- Compare this result with the expected result
You can use the ```TEST``` dictionary in your check's function to store the appropriate result for your check's test and return it to compare against the expected result. If you find it hard to understand, refer the existing checks.

For your test, maintain a dictionary of ```URLS``` that you will use as inputs for your check. Store the expected result for each particular URL as a value. You can use a list if you have multiple results for each URL.

Example:
```
def test_My_NewCheck(self):
	urls = {"https://google.com":"OK,'https://fruitdeal.in':"NOK"}
	checker = utils.Checks()
	# Write your code
	for url in urls:
		result = checker.My_NewCheck(url)
		self.assertEqual(result, urls[url], f"check failed for {url}")
```

## Pull Requests
You can create a pull request for your changes explaining clearly the changes you made and the reason for making the changes.
- For new check, name your pull request as,
```NEWCHECK_CHECKNAME```
- For new feature, 
```FEATURE_FEATURENAME```
- Bug fixes,
```BUG_DESCRIPTION```
