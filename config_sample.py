
# PEM file is the cert file I use to validate certificate authenticity.
PEM_FILE = 'cacert.pem'

# API URL is the same for every single API v2 request.
API_URL = 'https://api.ramcoams.com/api/v2/'

# This is a fake, non-working API key, yours has to be substituted here.
API_KEY = 'Ramcon01-Sandbox-Test-92asdfadfasdasdfdasdfaasdf8b';

#Association NRDS ID
ASSOC_NRDS = '1234'

#test user
ENROLL_ID = 'test_user999'
ENROLL_SECRET = 'asdfwe1232df'

#link to chaincode ID from EngagementOnChain Example , useful if you are developing against constantly changing chaindcode id's
with open('path/to/EngagementOnChain/deployLocal/chaincode_id', 'r') as f:
    CHAINCODE_ID = f.readline()

#local dev for mac
CORE_PEER_ADDRESS = 'http://192.168.99.100:7050' #or local host on linux

#bluemix dev
#CORE_PEER_ADDRESS = 'http://dxyz437283c177a33d4088e6-vp0.us.blockchain.ibm.com:5004'
