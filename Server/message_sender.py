"""
message_sender.py

SRS cross-reference: The purpose of this file is to satisfy the non-functional requirement referenced in our
SRS document in section 3.2.5.

SDD cross-reference: This functionality is referenced as fallAlertSms() in Interaction Diagram in section
3.5.1.

Description: This file houses the two main required functionalities of sending fall alert messages to the emergency contacts.
"""

import requests
import json
import time
import yaml
from twilio.rest import Client


conf = yaml.safe_load(open('../application.yml'))
account_sid = conf['account_sid']
auth_token = conf['auth_token']
client = Client(account_sid, auth_token)

service_sid = conf['service_sid']
environment_sid = conf['environment_sid']
asset_sid = conf['asset_sid']

from_number = conf['from_number']

verified_numbers = conf['verified_numbers']


def get_contacts() -> set:
    """
    Open contacts.txt and load them into an array. Then Performs
    set intersection on contacts and verified numbers so that texts
    are only sent to verified numbers.
    :return: contacts: list of configured verified phone #'s
    """

    with open('contacts.txt') as json_file:
        contacts = {str(num) for num in json.load(json_file)['contacts']}
    return contacts.intersection(verified_numbers)


def send_text_messages():
    """
    This function sends the fall detection text message to all emergency contacts
    stored in contacts.txt. This sends immediately after a fall occurs and then user will
    have to wait a few seconds to receive the image of the fall.
    """

    # Get contacts
    contacts = get_contacts()

    if len(contacts) == 0:
        return

    message_body = "C.L.E.R.N. Fall Detection System\n\n" \
                   + "A fall has been detected!\n\n" \
                   + "Please wait while we send you an image of the fall...\n"

    # Iterate over contacts and send a the text message to each one
    for contact in contacts:
        message = client.messages.create(
                                     body=message_body,
                                     from_='+1' + from_number,
                                     to='+1' + contact
                                  )
    print("Message(s) sent to: " + str(contacts))


def send_image_messages(file_name, file_path, content_type):
    """
    This function takes in a file and uploads it as an asset version to the Twilio assets api.
    Once the asset has been uploaded it then sends a message with that image and to all Twilio
    verified phone numbers in the contacts.txt file.
    :param content_type: content type of the the file to upload
    :param file_name: name of the file to upload
    :param file_path: path of the file to upload
    """

    # Get contacts
    contacts = get_contacts()

    # If contacts is empty don't bother doing anything else
    if len(contacts) == 0:
        return

    # File object that wraps the file itself along with some metadata
    content_type = 'jpeg' if content_type == 'jpg' else content_type
    files = {
        'Content': (file_name, open(file_path, 'rb'), 'image/' + content_type),
        'Path': (None, file_name),
        'Visibility': (None, 'public'),
    }


    # Post request to upload the file to an a new asset version
    response = requests.post(
        'https://serverless-upload.twilio.com/v1/Services/' + service_sid + '/Assets/' + asset_sid + '/Versions',
        files=files,
        auth=(account_sid, auth_token))

    # Creating build with previously created asset version
    build = client.serverless \
        .services(service_sid) \
        .builds \
        .create(asset_versions=response.json()['sid'])

    # Grabbing current status of build
    build_status = client.serverless \
        .services(service_sid) \
        .builds(build.sid) \
        .fetch() \
        .status

    # This ping's the build's status twice a second until it has finished building
    start_time = time.time()
    print("Building started...")
    while build_status != 'completed':
        build_status = client.serverless \
            .services(service_sid) \
            .builds(build.sid) \
            .fetch() \
            .status
        time.sleep(1 / 2)

    end_time = time.time()
    print("Completed in: " + str(end_time - start_time))

    # Deploy build
    deployment = client.serverless \
        .services(service_sid) \
        .environments(environment_sid) \
        .deployments \
        .create(build.sid) \

    print('Asset uploaded at path: https://clernimageserver-6543-clerndev.twil.io/' + file_name)

    # Iterate over contacts and send a the image message to each one
    for contact in contacts:
        message = client.messages.create(
                                     from_='+1' + from_number,
                                     media_url='https://clernimageserver-6543-clerndev.twil.io/' + file_name,
                                     to='+1' + contact
                                  )

    print("Image(s) sent to: " + str(contacts))

