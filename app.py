# C:\Dan\Data\Private Projects\Youtube Description Updater\app.py
# Dan Ronen 17/04/2020
# A simple Youtube description updater, by making a series of API calls to Youtube Data API v3. We are updating the
# description of each video of the user's uploads to a new description (or adding to the original description of each
# video).

# required imports
import pip._vendor.requests as requests
import json
import socket
import time
import sys
import webbrowser


class Client():
    def __init__(self, socket, address): # setting some of the socket settings, and buffer size for the amount 
        self.sock = socket               # of data I should expect to come in, as a byte-stream.
        self.addr = address
        self.buffer_size = 1024

    def processResponse(self):
        """
        Takes in the data, and parses it to get a dictionary of all the parameters returned
        by the response from Google (for now we are only returning the [code] parameter).
        """
        data = self.sock.recv(self.buffer_size).decode("utf-8")

        # parsing the data to get the parameters list...
        data = str.split(data, '\n')
        data = data[0]
        data = str.split(data, '?')
        data = data[1]
        data = str.split(data, '&')

        # creating a dictionary for the parameters...
        params = {}
        for param in data:
            param = param.split("=")
            params[param[0]] = param[1]

        return params["code"].strip() # only return the code parameter since it's need to get the token.


class YotubeDescriptionUpdater():

    def __init__(self):
        self.code = None            # setting some empty variables that will be changed later on.
        self.access_token = None
        self.new_description = ""
        self.add_to_original_description = None

        self.server_setup()                                     # running some  server setup for retrieving the code
        client_id, client_secret = self.read_client_details()   # later on and reading the client data/details, such
        self.client_id = client_id                              # that we can communicate with Google API.
        self.client_secret = client_secret

    def read_client_details(self, filename="client_details"):
        """read the client json details file"""
        print("Getting Google API client details...\n")
        filename = filename+".json"
        with open('env/'+filename) as file_obj:
            client_details = json.load(file_obj)
        return client_details["client_id"], client_details["client_secret"]

    def server_setup(self):
        """
        initiates all variables realted to server functionality
        """
        print("Setting server parameters...\n")
        self.address = "localhost"              # These settings are crucial for the socket to be able to read responses
        self.port = 3333                        # and control how long we are willing to wait for a response.
        self.build_socket(timeout=120)          # 3 minutes in this case.

    def set_add_to_original_description(self, boolean):
        """
        sets the value for the add_to_original_description variable.
        """
        try:
            self.add_to_original_description = bool(boolean)     # just simple verification that the input is indeed
        except TypeError:                                        # the correct type of data we want.
            print("Incorret type assigned to variable")
            raise TypeError

    def get_user_input(self):
        """
        Ask the user for the desired new description, and if we keep or replace the original description.
        """
        new_description = input("What is going to be the new description? ")  # This will set the new Youtube description
        self.set_new_description(new_description)

        response = input("Add to the original description ([Y/y]/[N/n])? ")   # A simple while loop to force the user to input
        while response.upper() != "N" and response.upper() != "Y":            # a 'Y'/'y' or 'N'/'n' to set the setting.
            
            print("Please use Y or N to choose.") 
            response = input("Add to the original description ([Y/y]/[N/n])? ")
            if response.upper() == "Y":
                self.set_add_to_original_description(True)
            if response.upper() == "N":
                self.set_add_to_original_description(False)
                       

    def set_new_description(self, string):
        """
        Sets the variable new_description to the input string.
        """
        self.new_description = str(string)

    def run(self):
        """
        This runs the chain of commands/methods/function that need to run to update the description.
        """
        try:
            self.get_user_input()          # The functions raise errors if any of the stages fail, so we capture it 
            self.getUserConsent()          # and then make sure to disable to access token, such that we don't have
            self.get_code()                # an overflow of tokens that are able to completly change a user's Youtube
            self.get_access_token()        # account.
        except:
            print("Some errors hav occured attempting to complete the first stages.")
            print("Canceling")
            return
        try:
            uploads = self.get_upload_ids()
            self.updateVideos(uploads)
        except:
            print("Failed to run Youtube Description Updater.")
        self.disable_access_token()
        

    def build_url(self, url, payload=None):
        """
        if the payload is not None, then it will return the url with the added payloads.
        """
        if payload is None:
            return url
        else:
            keys_array = tuple(payload.keys())           # This part essentially takes a dictioary of paramters
            payload_length = len(payload)                # and a URL, converts them into a GET request for it
            payload_array = [""] * payload_length        # to be opened in the browser.
            url += "?"
            for i in range(payload_length):
                key = keys_array[i]
                key_value = payload[key]
                payload_array[i] = f"{key}={key_value}"

            url += "&".join(payload_array)
            
            return url

    def getUserConsent(self):
        """
        Opening the user's browser to get the user to provide premission for there youtube
        account to be accsessed. This gives us the token from the google API service.
        """
        url = "https://accounts.google.com/o/oauth2/v2/auth"
        payload = {
            "scope": "https://www.googleapis.com/auth/youtube.force-ssl",
            "response_type": "code",
            "redirect_uri": f"http://{self.address}:{self.port}",
            "client_id": self.client_id
        }
        print("Opening url in browser. Please accept to proceed.")
        time.sleep(2)
        webbrowser.open_new_tab(self.build_url(url, payload=payload))

    def build_socket(self, timeout=None):
        """
        creates the socket and data related to it.
        """
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serversocket.bind((self.address, self.port))  # These settings set the socket to IPv4 and to expect a
                                                           # constant stream of data, as a response. The bind function
        if timeout:                                        # sets the socket addres + port, so it knows where to wait
            self.set_socket_timeout(timeout)               # for a response from.

    def set_socket_timeout(self, timeout):
        try:
            timeout = float(timeout)                       # This sets the server socket timeout, which just says how
            if timeout >= 0:                               # long its gonna wait for a response since its intiated to
                self.serversocket.settimeout(timeout)      # accept one.
            else:
                print("Timeout value must be positive or zero (integers).")
        except:
            print("Timeout value must be a float or int.")

    def get_code(self):
        """
        retreive the user unique code to retreive the access token for the user's account 
        """

        self.serversocket.listen(0)                     # start listening for connection requests, and keep a backlog of 0
                                                        # Once we run the accept() method, we get the client that is connecting
        print("Loopback server started, and awaiting permission.") # to us socket address and socket object. This is then
        clientsocket, address = self.serversocket.accept()         # proccessing at the Client object.

        client = Client(clientsocket, address)
        self.code = client.processResponse()

        self.serversocket.close() # Making sure we close the conncetion after we are done using it.

    def get_access_token(self):
        """
        Get the access token to perform actions from the Google API
        """
        url = 'https://www.googleapis.com/oauth2/v4/token' # These are the needed parameters by the Google API
        payload = {                                        # to get the access token back.
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            "redirect_uri": f'http://{self.address}:{self.port}',
            'code': self.code,
            'grant_type': 'authorization_code'
        }

        request = requests.post(url, params=payload)

        if request.status_code == 200:
            try:
                responseJSON = request.json()
                self.access_token = responseJSON['access_token']   # To procceed, we must get a 200 (OK) response, and
            except ValueError:                                     # it must be of JSON format. And must include the 
                print('Response of wrong type (non-JSON).')        # access token. Otherwise we raise an error.
                raise ValueError
        else:
            print('An error has occured!')
            print(request.content.decode("utf-8"))
            raise

    def disable_access_token(self):
        """
        Disables the access token used to call the authorized API calls.
        """
        payload = {
            'token': self.access_token
        }
        disabled_token = False
        attempts_allowed, attempts_count = 5, 0                              # Given a Google API error, we want to at least
                                                                             # try 5 times or so to disable the token, since
        while disabled_token == False and attempts_count < attempts_allowed: # if lost it can cause some serious damage. So a
            r = requests.post(                                               # while loop, to try and revoke the token (5 times).
                'https://accounts.google.com/o/oauth2/revoke', params=payload) # Otherwise it's gonna raise an excpetion, so the 
                                                                             # user is aware of the potential risk, and problem. 
            if r.status_code == 200:
                print("\nToken successfully revoked")
                disabled_token = True
            elif attempts_count < attempts_allowed:
                print(f"Attempt {attempts_count} to revoke token failed...")
                attempts_count += 1
            else:
                print("\nToken revocation has failed... \n")
                raise Exception

    def get_upload_ids(self):
        """
        Request from the Google API to get the uploads playlist id, and then get the ids of all the
        videos in the playlist.
        """

        url = 'https://www.googleapis.com/youtube/v3/channels'
        payload = {
            'access_token': self.access_token,
            'part': 'contentDetails',
            'mine': 'true'
        }

        r = requests.get(url, params=payload)
        # print(r)
        if r.status_code == 200:
            try:
                responseJSON = r.json()          # This get the uploads playlist id, so we can get the videos we want to update
                # print(responseJSON)
                uploads_playlist_id = responseJSON['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            except ValueError:
                print("Incorrect response type (not JSON).")
                raise ValueError
        else:
            print(r.content.decode('utf-8'))

        # requesting videos IDs
        url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        payload = {
            'access_token': self.access_token,
            'part': 'contentDetails',
            'playlistId': uploads_playlist_id
        }
        r = requests.get(url, params=payload)

        if r.status_code == 200:
            try:
                responseJSON = r.json()
                videos_JSON = responseJSON['items']              # This returns a list of JSON objects that contain
            except:                                              # The ids of all the videos that we are going to change
                print("Incorrect response type (not JSON).")
                raise ValueError
        else:
            print(r.content.decode("utf-8"))
            raise ValueError

        video_ids = ", ".join(video["contentDetails"]["videoId"]  # This converts the list of video objects into a string
                              for video in videos_JSON)           # of video ids, sperated by a comma and space (', ').
        return self.get_video_details(video_ids)                  # This is because the next call to get the video details,
                                                                  # requires this for a bulk request of video details.
    def get_video_details(self, video_ids):
        """
        Gets the required details to update the snippet data
        """
        url = "https://www.googleapis.com/youtube/v3/videos"
        payload = {
            "access_token": self.access_token,
            "part": "snippet",
            "id": video_ids                                       # A list of ids sperated by commas.
        }

        r = requests.get(url, params=payload)

        if r.status_code == 200:
            try:
                responseJSON = r.json()
            except ValueError:
                print("Incorrect format returned (not JSON).")
        else:
            print("An error has occured")
            print(r.error)
            raise Exception
                                                                    # Here we are creating a dictionary of details for each video id
        videos = {}                                                 # These are required by the API to change the description, and
        for video in responseJSON["items"]:                         # current description is for if we want to keep, and add to the
            videos[video["id"]] = {"title": video["snippet"]["title"], # original description.
                                   "categoryId": video["snippet"]["categoryId"],
                                   "currentDesc": video["snippet"]["description"]}

        return videos

    def updateVideos(self, videos):
        """
        updates the description of all your videos
        """
        failed = {}
        amount_of_videos = len(videos)

        if amount_of_videos <= 0:
            print("There are no videos to update...")
        else:
            url = 'https://www.googleapis.com/youtube/v3/videos'
            payload = {
                "access_token": self.access_token,
                "part": "snippet",
                "scope": "https://www.googleapis.com/auth/youtube.force-ssl"
            }
            # progress bar to know how many more videos we have left to go.
            progress_count = 0
            sys.stdout.write("[%s]" % (" " * amount_of_videos))
            sys.stdout.flush()
            # return to start of line, after '['
            sys.stdout.write("\b" * (amount_of_videos+1))

            for video_id in videos.keys():                          # Here we are simply calling the Google API, to update
                video_snippet = videos[video_id]                    # the descriptions of each video in the videos dictionary
                data = {                                            # that we created in get_video_details() for each video id.
                    "id": video_id,
                    "kind": "youtube#video",
                    'snippet': {
                        'title': video_snippet["title"],
                        'categoryId': video_snippet["categoryId"]   # Below we are choosing a new description that we want.
                    }                                               # This depends on the setting of add_to_original_description
                }                                                   # (keep or replace).
                if self.add_to_original_description:   
                    data['snippet']['description'] = video_snippet["currentDesc"] + "\n" + self.new_description 
                else:
                    data['snippet']['description'] = self.new_description

                r = requests.put(url, json=data, params=payload)
                if r.status_code != 200:
                    failed[video_id] = video_snippet        # We are also keep a dictionary of all the failed cases to update a video 

                sys.stdout.write("█") # Simply incrementing the progress bar by one per video proccessed.
                sys.stdout.flush()
            sys.stdout.write("]\n")   # Closing up the progress bar.

            if len(failed) > 0:
                print("Some videos failed to update:")
                print(failed)

            print("Update complete!")


if __name__ == "__main__":
    obj = YotubeDescriptionUpdater()
    obj.run()
