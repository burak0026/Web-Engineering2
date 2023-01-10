import os
import requests
import jwt
import json
from flask import Response
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def validate_jwt(token,app):
    if token is None:
        app.logger.error('JWT not Found')
        return Response("token not found", status=401)
    #get public key from Keycloak
    keycloak_url = f"http://{os.getenv('KEYCLOAK_HOST')}/auth/realms/{os.getenv('KEYCLOAK_REALM')}"
    keycloak_request = requests.get(keycloak_url)
    keycloak_request_json = json.loads(keycloak_request.text)
    keycloak_pubkey = keycloak_request_json["public_key"]
    #check if key is present, else throw 401
    if keycloak_pubkey is None:
        app.logger.error('Public key not Found')
        return  Response("public key not found", status=401)
    #add header/footer to public key and serialize
    keycloak_pubkey = "-----BEGIN PUBLIC KEY-----\n"+keycloak_pubkey+"\n-----END PUBLIC KEY-----"
    keycloak_pubkey = serialization.load_pem_public_key(bytes(keycloak_pubkey,'UTF-8'),default_backend)
    #check if token is valid
    try:
        jwt.decode(token,keycloak_pubkey,algorithms=["RS256"],audience="account")
        return True
    except Exception:
        app.logger.error('invalid Token')
        return Response("invalid token", status=401)
