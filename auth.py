from functools import lru_cache
from typing import Annotated

import jwt
import requests
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from conf import settings


@lru_cache()
def get_openid_configuration():
    return requests.get(
        settings.openid_configuration, timeout=10
    ).json()


@lru_cache()
def get_jwks_client():
    return jwt.PyJWKClient(uri=get_openid_configuration()["jwks_uri"])


security = HTTPBearer()


def get_user(token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    openid_configuration = get_openid_configuration()
    jwks_client = get_jwks_client()

    signing_key = jwks_client.get_signing_key_from_jwt(token.credentials)
    decoded_jwt = jwt.decode(
        token.credentials,
        key=signing_key.key,
        algorithms=openid_configuration["id_token_signing_alg_values_supported"],
        options={"verify_aud": False},
    )

    return decoded_jwt["sub"]
