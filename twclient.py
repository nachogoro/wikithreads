import oauth2 as oauth
import pickle
import time
import twitter
import urllib.parse as urlparse
import webbrowser

'''
#################################################
##########                             ##########
########## USE YOUR OWN KEY AND SECRET ##########
##########                             ##########
#################################################
'''
CONSUMER_KEY = 'CHANGEME'
CONSUMER_SECRET = 'CHANGEME'
CREDENTIALS_FILE = '.twitter-credentials.db'


def _load_credentials_from_file():
    try:
        with open(CREDENTIALS_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None


def _store_credentials_to_file(credentials):
    with open(CREDENTIALS_FILE, 'wb') as f:
        pickle.dump(credentials, f)


def get_access_token(consumer_key, consumer_secret):
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to
    # obtain said access token.
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.
    webbrowser.open(
        '{}?oauth_token={}'.format(
            authorize_url,
            request_token['oauth_token'.encode('utf-8')].decode('utf-8')))

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    oauth_verifier = input('PIN: ')

    # Step 3: Once the consumer has redirected the user back to the
    # oauth_callback URL you can request the access token the user has
    # approved.  You use the request token to sign this request. After this is
    # done you throw away the request token and use the access token returned.
    # You should store this access token somewhere safe, like a database, for
    # future use.
    token = oauth.Token(
        request_token['oauth_token'.encode('utf-8')].decode('utf-8'),
        request_token['oauth_token_secret'.encode('utf-8')].decode('utf-8'))
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    return access_token


def post_as_thread(tweets, use_stored_credentials):
    '''
    Takes a list of strings of less than 140 characters and posts them as a
    thread in Twitter.
    '''
    # See if we already have credentials
    access_token = None
    if use_stored_credentials:
        access_token = _load_credentials_from_file()

    if not access_token:
        access_token = get_access_token(CONSUMER_KEY, CONSUMER_SECRET)

    _store_credentials_to_file(access_token)

    api = twitter.Api(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        access_token['oauth_token'.encode('utf-8')].decode('utf-8'),
        access_token['oauth_token_secret'.encode('utf-8')].decode('utf-8'))
    api.VerifyCredentials()

    # Post the first tweet of the thread
    print('Subiendo tweet 1 de {}\r'.format(len(tweets)))
    status = api.PostUpdate(tweets[0])

    # The longer the thread, the longer we should wait between API calls to not
    # exceed the limit. This should really be done by querying the API rate
    # limit.
    sleep_time = 10 if len(tweets) < 20 else 30

    for index, tweet in enumerate(tweets[1:]):
        # Wait and add the next tweet
        time.sleep(sleep_time)
        print('Subiendo tweet {} de {}\r'.format(index+2, len(tweets)))
        status = api.PostUpdate(tweet, in_reply_to_status_id=status.id)
