# YoutubeDescriptionUpdater

This is a pet project from 2019, which uses `requests` module to perform REST API requests to Google.
The result of the requests are that all the user's videos description are updated.

This entails either replacing or add to your description. This project eventually was discontinued in
17/04/2020 once I began to grow more interest in other side projects. 
The final steps remaining for the project include moving from a terminal interface to a GUI of some kind.

Running the project (10/11/2020):
1. To run the project you will need to verify that requests module is installed (`pip3 install requests`).
2. You will need Google API credentials in a `env/client_details.json` file. This is used for communicating with the Google API.
3. run `python3 app.py`