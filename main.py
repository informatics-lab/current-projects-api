#! /bin/env python

import os
import requests
from flask import Flask
from flask_cors import CORS, cross_origin
import json

CARDS_IMAGE_CACHE = {}
MEMBERS_CACHE = {}

AUTH = {'key': os.environ['API_KEY'],
        'token': os.environ['API_TOKEN']}
DONT_PUBLICISE_LABEL = 'private'


app = Flask(__name__)
CORS(app)


def hit_member_api(memberID):
    try:
        url = 'https://api.trello.com/1/members/'+ memberID
        response = requests.get(url, params=AUTH)
        trello_member = response.json()
        member_name = trello_member['fullName']
    except:
        member_name = None
    try:
        member_image = 'https://trello-avatars.s3.amazonaws.com/'+trello_member['avatarHash']+"/170.png"
    except TypeError:
        member_image = None
    return {"name": member_name, "image": member_image}


def get_member(memberID):
    try:
        member = MEMBERS_CACHE[memberID]
    except KeyError:
        member = hit_member_api(memberID)
        MEMBERS_CACHE[memberID] = member
    return member

    
def hit_card_image_api(cardID, attachmentID):
    url = 'https://api.trello.com/1/cards/'+cardID+'/attachments/'+attachmentID
    response = requests.get(url, params=AUTH)
    image_data = response.json()
    return image_data['url']


def get_card_image(cardID, attachmentID):
    try:
        image_url = CARDS_IMAGE_CACHE[cardID+attachmentID]
    except KeyError:
        image_url = hit_card_image_api(cardID, attachmentID)
        CARDS_IMAGE_CACHE[cardID+attachmentID] = image_url
    return image_url


def get_active_projects():
    url = 'https://api.trello.com/1/lists/'+ os.environ['ACTIVE_PROJECTS_LIST_ID'] +'/cards'
    response = requests.get(url, params=AUTH)
    response.raise_for_status()

    cards = response.json()
    
    output = []
    
    for card in cards:
        if DONT_PUBLICISE_LABEL not in [label['name'] for label in card['labels']]:
            this_output = {}
            this_output['project_name'] = card['name']
            this_output['project_image'] = get_card_image(card['id'], card['idAttachmentCover'])
            this_output['members'] = [get_member(memberID) for memberID in card['idMembers']]
            output.append(this_output)

    return output


@app.route("/current-projects/")
def get_active_projects_json():
    result = get_active_projects()
    print(result)
    return json.dumps(result)


if __name__=="__main__":
    print(get_active_projects_json())
