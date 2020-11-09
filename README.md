# YoutubeDescriptionUpdater

This is a Youtube Description Updater. This allows you to go through all your youtube videos and update the descriptions.
This uses webbrowser, requests, and some socket programming skills.

This was originally written in 28/06/2019. However, I decided to drop the project after 17/04/2020. This is because I have
learned enough skils using REST API requests and some socket programming that allowed me to be happy with my learning experience.

Running the project (as of 10/11/2020):
1. To run the project you will need to provide a `/env/client_details.json` file, which contains a google API client_id and client_secret.
Otherwise you will not be able to run the project.
2. Once you have those details set up, simply clone the project and ensure that you have installed the requests library
  - This is done using `pip3 install requests`.
3. Simply then run the application using `python3 app.py`.
