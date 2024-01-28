# StravaScraper

https://developers.strava.com/docs/getting-started/
https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities-0

http://www.strava.com/oauth/authorize?client_id=<CLIENTID>&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all

curl -X POST https://www.strava.com/oauth/token \
	-F client_id=YOURCLIENTID \
	-F client_secret=YOURCLIENTSECRET \
	-F code=AUTHORIZATIONCODE \
	-F grant_type=authorization_code
