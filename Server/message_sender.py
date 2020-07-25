"""
message_sender.py

SRS cross-reference: The purpose of this file is to satisfy the non-functional requirement referenced in our
SRS document in section 3.2.5.

SDD cross-reference: This functionality is referenced as fallAlertSms() in Interaction Diagram in section
3.5.1.

Description: This file houses the two main required functionalities of sending fall alert SMS to the emergency contacts.
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


def upload_new_asset(file_name, file_path):
    """
    This function takes in a file and uploads it as an asset version to the Twilio assets api
    so that the send_messages() function can access the file via a media_url.
    :param file_name: name of file to upload as an asset to Twilio's service
    :param file_path: file path of file to upload as an asset to Twilio's service
    :return: file_name: a str that is the name of the file that was uploaded
    """


    # File object that wraps the file itself along with some metadata
    files = {
        'Content': (file_name, open(file_path, 'rb'), 'image/png'),
        'Path': (None, file_name),
        'Visibility': (None, 'public'),
    }

    # Post request to upload the file to an a new asset version
    response = requests.post('https://serverless-upload.twilio.com/v1/Services/'+service_sid+'/Assets/'+asset_sid+'/Versions',
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
        time.sleep(1/2)

    end_time = time.time()
    print("Completed in: " + str(end_time - start_time))

    # Deploy build
    deployment = client.serverless \
                       .services(service_sid) \
                       .environments(environment_sid) \
                       .deployments \
                       .create(build.sid) \

    print('Asset uploaded at path: https://clernimageserver-6543-clerndev.twil.io/' + file_name)
    return file_name


def send_text_messages():
    """
    This function sends the fall detection text message to all emergency contacts
    stored in contacts.txt. This sends immediately after a fall occurs and then user will
    have to wait a few seconds to receive the image of the fall.
    """

    # Open contacts.txt and load them into an array
    with open('../Client/contacts.txt') as json_file:
        contacts = json.load(json_file)['contacts']

    message_body = "C.L.E.R.N. Fall Detection System\n\n" \
                   + "A fall has been detected!\n\n" \
                   + "Please wait while we send you an image of the fall...\n"

    # Iterate over contacts and send a the text message to each one
    for contact in contacts:
        message = client.messages.create(
                                     body=message_body,
                                     from_='+1' + from_number,
                                     to='+1' + str(contact)
                                  )
    print("Message(s) sent to: " + str(contacts))


def send_image_messages(obj):
    """
    This takes an obj that contains a fall_id (a.k.a. the file name of the frame when a fall occurred)
    and sends a message with that image and to all Twilio verified phone numbers in the contacts.txt file.
    :param obj: the result object returned from the thread's submit() method (meant to contain
    the file_name returned from upload_new_asset)
    """

    # Open contacts.txt and load them into an array
    with open('../Client/contacts.txt') as json_file:
        contacts = json.load(json_file)['contacts']

    # Iterate over contacts and send a the image message to each one
    for contact in contacts:
        message = client.messages.create(
                                     from_='+1' + from_number,
                                     media_url='https://clernimageserver-6543-clerndev.twil.io/' + obj._result,
                                     to='+1' + str(contact)
                                  )

    print("Image(s) sent to: " + str(contacts))


