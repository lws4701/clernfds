# clernfds - A Video-Based Fall Detection System

## CLERN Development Team
* Noah Elliott
* Chris Hinson
* Ethan Lynch
* Ryan Schildknecht
* Lewis Smith


## FOR TESTING CLERN FDS

### Installing Dependencies
Use python's pip module to install the following dependencies:
* opencv-contrib-python
* pyyaml
* phonenumbers
* twilio

### Opening the Server
1. Navigate to clernfds root directory
4. Double click the file "clern_fds_server.py" inside the "Server" folder.

### Opening the Client (Production Client)
1. Start the server
3. Double click the file "clern_fds.py" inside the "Client" folder.

### Opening the Client (For running against test videos)
1. Start the server
2. Unpack test_videos.zip into clernfds/Client/test
3. Modify line 16 in Client/test/test_clern.py to point to the desired test video
4. Double click the file "test_clern.py" in the "test" folder inside the "Client" folder.
5. Repeat Steps 3-4 as desired
