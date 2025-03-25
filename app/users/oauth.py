import os
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth
import requests

# Fetch LinkedIn's OpenID configuration dynamically
openid_config_url = "https://www.linkedin.com/oauth/.well-known/openid-configuration"
openid_config = requests.get(openid_config_url).json()

LINKEDIN_AUTH_URL = openid_config["authorization_endpoint"]
LINKEDIN_TOKEN_URL = openid_config["token_endpoint"]
LINKEDIN_USER_INFO_URL = openid_config["userinfo_endpoint"]


load_dotenv()

oauth = OAuth()

# oauth.register(
#     name='google',
#     client_id=os.getenv(''),
#     client_secret=os.getenv(''),
#     authorize_url=os.getenv(''),
#     token_url=os.getenv(''),
#     client_kwargs={'scope': 'openid email profile'}
# )

oauth.register(
    name='linkedin',
    client_id='861iuo5bvnbmix',
    client_secret='WPL_AP1.Y63U5HoLsSaiaTVe.5otgFA==',
    authorize_url=LINKEDIN_AUTH_URL,   # From OpenID config
    token_url=LINKEDIN_TOKEN_URL,      # From OpenID config
    userinfo_endpoint=LINKEDIN_USER_INFO_URL,  # From OpenID config
    client_kwargs={"scope": "openid email profile"},
)