# clernfds - A Video-Based Fall Detection System

## CLERN Development Team
* Noah Elliott
* Chris Hinson
* Ethan Lynch
* Ryan Schildknecht
* Lewis Smith


## FOR TESTING CLERN FDS
### Opening the Server
1. Open Command Prompt Window
2. Navigate to clernfds root directory
3. Execute the command "call clernfds/venv/Scripts/Activate.bat"
4. Execute the command "py Server/clern_fds_server.py"

### Opening the Client (Production Client)
1. Start the server
2. Perform steps 1-3 in the section "Opening the Server"
3. Execute the command "py Client/clern_fds.py"

### Opening the Client (For running against test videos)
1. Start the server
1. Unpack test_videos.zip into clernfds/Client/test
2. Perform steps 1-3 in the section "Opening the Server"
3. Modify line 16 in Client/test/test_clern.py to point to the desired test video
4. Execute the command "py Client/test/test_clern.py"
5. Repeat Steps 3-4 as desired
