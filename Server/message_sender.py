import requests
import json
import time
from twilio.rest import Client


account_sid = 'AC5fc3bbbccf59dca7e2ea7fe531c97729'
auth_token = '253e1b8798275817983dee9d1720fe58'
client = Client(account_sid, auth_token)

service_sid = 'ZS11a28c3e928b3e447cad16682d17bf51'
environment_sid = 'ZEb5540d5b3e615da9e28755fddc390dad'
asset_sid = 'ZH76acf682588fb622cf276c5c86f04931'

domain_name = 'clernimageserver-6543-clerndev.twil.io'

def upload_new_asset(file_path, file_name):

    files = {
        'Content': (file_name, open(file_path, 'rb'), 'image/png'),
        'Path': (None, file_name),
        'Visibility': (None, 'public'),
    }

    response = requests.post('https://serverless-upload.twilio.com/v1/Services/ZS11a28c3e928b3e447cad16682d17bf51/Assets/ZH76acf682588fb622cf276c5c86f04931/Versions',
                             files=files,
                             auth=('AC5fc3bbbccf59dca7e2ea7fe531c97729', '253e1b8798275817983dee9d1720fe58'))

    print(str(response.json()))
    print("asset_version_sid: " + response.json()['sid'])

    build = client.serverless \
                  .services(service_sid) \
                  .builds \
                  .create(asset_versions=[response.json()['sid']])

    print("build_sid: " + build.sid)

    build_status = client.serverless \
                         .services(service_sid) \
                         .builds(build.sid) \
                         .fetch() \
                         .status

    start_time = time.time()
    while build_status != 'completed':
        build_status = client.serverless \
                             .services(service_sid) \
                             .builds(build.sid) \
                             .fetch() \
                             .status
        print(build_status)
        time.sleep(1/2)

    end_time = time.time()
    print("Completed in: " + str(end_time - start_time))

    deployment = client.serverless \
                       .services(service_sid) \
                       .environments(environment_sid) \
                       .deployments \
                       .create(build.sid) \

    print("deployment_sid: " + deployment.sid)
    print("Asset uploaded at path: " + "https://" + domain_name + "/" + file_name)



def send_messages():

    with open('contacts.txt') as json_file:
        contacts = json.load(json_file)['contacts']

    print(contacts)

    for contact in contacts:
        message = client.messages.create(
                                     body="A fall has been detected!",
                                     from_='+12028662717',
                                     media_url=['https://clernimageserver-6543-clerndev.twil.io/fall-01-cam0-rgb-035.png'],
                                     to='+1' + str(contact)
                                  )
        print(message.sid)

