#!/usr/bin/python
"""
This sample should ping ramco API for a changes in committee membership and post to a hyperledger blockchain.
David Conroy, 2017
"""
import config
import requests
from urllib import urlencode
import json
import base64
import logging
import sys
import os
from io import BytesIO
from binascii import hexlify

# set up logging
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

root.addHandler(ch)
logging.basicConfig(level=logging.INFO)

committee_data = {}
committee_memberships = {}
committee_data = {}

# ramco fuctions
def sendMessage(ramcodata):

    r = requests.post(config.API_URL, verify=config.PEM_FILE, data=ramcodata)
    return (json.loads(r.text))


def fetch_committee_changes():

    payload = {'key': config.API_KEY, 'Operation': 'GetEntities', 'Entity': 'cobalt_committeemembership',
               'Attributes': 'cobalt_name,cobalt_committeeid,cobalt_contactid,cobalt_termenddate,cobalt_termbegindate,cobalt_contact_cobalt_committeemembership/cobalt_nrdsid,cobalt_contact_cobalt_committeemembership/firstname,cobalt_contact_cobalt_committeemembership/lastname', 'Filter': 'CreatedOn<ge>2016-03-01'}
    results = sendMessage(payload)
    logging.info(
        "Found " + str(len(results['Data'])) + " Altered Committee Memberships in RAMCO:")

    return results['Data']


# chaincode functions
def login_chain(enrollId, enrollSecret):

    payload = {"enrollId": enrollId,
               "enrollSecret": enrollSecret}
    r = requests.post(config.CORE_PEER_ADDRESS +
                      "/registrar", data=json.dumps(payload))

    return r.text


def query_thing(id):
    payload = {
        "jsonrpc": "2.0",
        "method": "query",
        "params": {
            "type": 1,
            "chaincodeID": {
                  "name": config.CHAINCODE_ID
            },
            "ctorMsg": {
                "function": "get_thing",
                "args": [
                    id
                ]
            },
            "secureContext": config.ENROLL_ID
        },
        "id": 1
    }

    r = requests.post(config.CORE_PEER_ADDRESS +
                      "/chaincode", data=json.dumps(payload))

    return r.json()


def does_user_exist(id):
    logging.info("checking if user exists: " + id)
    results = query_user(id)
    print(results)
    try:
        if (results["result"]["status"] == "OK"):
            logging.info("Update User ")
            return True

    except:
        return False


def does_thing_exist(id):
    results = query_thing(id)
    try:
        if (results["result"]["status"] == "OK"):
            return True
    except Exception as e:
        print(e)
        return False


def query_user(id):
    payload = {
        "jsonrpc": "2.0",
        "method": "query",
        "params": {
            "type": 1,
            "chaincodeID": {
                  "name": config.CHAINCODE_ID
            },
            "ctorMsg": {
                "function": "get_user",
                "args": [
                    id
                ]
            },
            "secureContext": config.ENROLL_ID
        },
        "id": 1
    }

    r = requests.post(config.CORE_PEER_ADDRESS +
                      "/chaincode", json.dumps(payload))

    return r.json()


def create_thing_in_chain(thing):
    thing = json.dumps(thing, ensure_ascii=False)
    logging.info(thing)
    payload = {
        "jsonrpc": "2.0",
        "method": "invoke",
        "params": {
            "type": 1,
            "chaincodeID": {
                "name": config.CHAINCODE_ID
            },
            "ctorMsg": {
                "function": "add_thing",
                "args": [
                    thing
                ]
            },
            "secureContext": config.ENROLL_ID
        },
        "id": 1
    }
    print(payload)
    r = requests.post(config.CORE_PEER_ADDRESS + "/chaincode",
                      json.dumps(payload))
    print(r.text)
    return r.text


def update_thing_in_chain(thing):
    payload = {
        "jsonrpc": "2.0",
        "method": "invoke",
        "params": {
            "type": 1,
            "chaincodeID": {
                "name": config.CHAINCODE_ID
            },
            "ctorMsg": {
                "function": "update_thing",
                "args": [
                    thing
                ]
            },
            "secureContext": config.ENROLL_ID
        },
        "id": 1
    }
    print(payload)
    r = requests.post(config.CORE_PEER_ADDRESS + "/chaincode",
                      json.dumps(payload))
    print(r.text)
    return r.text


def main():
    logging.info('Started')
    login_chain(config.ENROLL_ID, config.ENROLL_SECRET)

    committee_memberships = {}
    committee_data = {}

    for committee_members in fetch_committee_changes():
        try:
            thing_exists = False
            person_exists = False
            #print (committee_members)
            committee_data["firstName"] = committee_members[
                "cobalt_contact_cobalt_committeemembership"]["FirstName"]
            committee_data["lastName"] = committee_members[
                "cobalt_contact_cobalt_committeemembership"]["LastName"]
            committee_data["Assoc_id"] = config.ASSOC_NRDS
            committee_data["Description"] = committee_members[
                "cobalt_CommitteeId"]["Display"]
            committee_data["NRDS"] = committee_members[
                "cobalt_contact_cobalt_committeemembership"]["cobalt_NRDSID"]
            committee_data["Date"] = committee_members[
                "cobalt_TermEndDate"]["Display"]
            committee_data["id"] = committee_members[
                "cobalt_CommitteeId"]["Value"]
            committee_data["name"] = committee_members[
                "cobalt_name"]

            # committee_data["id"]=hexlify(os.urandom(16)).decode('ascii')
            logging.info("Checking if \"" + committee_data[
                         "name"] + "\" already exists on the Blockchain: " + committee_data["id"])
            if (does_thing_exist(committee_data["id"])):
                logging.info("...already exists on the Blockchain")
                thing_exists = True
            else:
                logging.info(committee_data[
                             "name"] + " does not exist. Creating Blockchain Entry...")
                thing = {"id": committee_data["id"],
                         "description": committee_data["Description"],
                         "date": committee_data["Date"],
                         "assoc_id": committee_data["Assoc_id"]}
                create_thing_in_chain(thing)
                thing_exists = True

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
