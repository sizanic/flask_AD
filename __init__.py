from flask import Flask, jsonify, request, render_template
import time, requests
from collections import deque
from datetime import datetime


# parametrage serveur Alwaysdata
# Configuration avancée
# Paramètres supplémentaires uWSGI
# processes = 1
# cheaper = 0

# flask_AD/env/pyvenv.cfg
# include_system_site_packages = true


app = Flask(__name__)                                                                                                                  

LOG = deque()

API_KEYS = deque([
    "jBPsVp8uk5s7o7ibrGfM",        # vPasteStream    // OK  01/09/2025 03:50
    "TKftCdvxhrU2abyNnpNQ",        # clyrkakenta     // OK  09/08/2025 12:16 (shanbox.izanic)
    "YTlkoKj3gxGHQ9XT9mHk",        # shansblock      // OK  16/08/2025 01:57
    "JpldxPIQ8ng7camNNH3n"         # sizanic         // OK  26/07/2025 19:35
])
last_request_time = time.time()


   
@app.route('/')
def hello_world():
    now = time.time()
    return "LOG du %s<br><br>%s" % (datetime.fromtimestamp(now).strftime('%d-%m-%Y %H:%M:%S'), "<br>".join(LOG))

    #render_template('hello.html')

# /debrid?apikey=%s&link=%s
@app.route('/debrid', methods=['GET'])
def debrid():
    global last_request_time
    #apikey = request.args.get('apikey')
    link = request.args.get('link')

    now = time.time()
    if not link or (not 'alldebrid' in link and not '1fichier' in link):
        formatted_time = datetime.fromtimestamp(now).strftime('%d-%m-%Y %H:%M:%S')
        LOG.append('%s - redirect %s' % (formatted_time, link))
        return jsonify({"status": "error", "error": {"code": "LINK_HOST_NOT_SUPPORTED", "message": "LINK_HOST_NOT_SUPPORTED"}})

    time_per_key = 46 / len(API_KEYS)
    if now - last_request_time < time_per_key:
        last_request_time += time_per_key
        time.sleep( last_request_time - now)
    else:
        last_request_time = now

    apikey = API_KEYS.popleft()

#	url = "http://api.alldebrid.com/v4/link/unlock?agent=vStreamRedirect&apikey=%s&link=%s"
    url = "http://api.alldebrid.com/v4/link/unlock"
    params = {
        "agent": 'vStreamRedirect',
        "apikey": apikey,
        "link": link
    }
    
    # Envoi de la requête GET avec paramètres
    try:
        formatted_time = datetime.fromtimestamp(now).strftime('%d-%m-%Y %H:%M:%S')
        LOG.append('%s - %s' % (formatted_time, apikey))
        response = requests.get(url, params=params)
        if any(error in response.text for error in ["AUTH_USER_BANNED", "AUTH_BAD_APIKEY", "MUST_BE_PREMIUM"]):
            formatted_time = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
            LOG.append('%s - %s -> %s' % (formatted_time, apikey, response.text))
            return debrid()  # réessaie avec une autre clé
        API_KEYS.append(apikey)    # on replace la key à la fin car elle est toujours valide
        data = response.json()
    except Exception as e:
        API_KEYS.append(apikey)
        formatted_time = datetime.fromtimestamp(now).strftime('%d-%m-%Y %H:%M:%S')
        LOG.append('%s -> %s' % (formatted_time, str(e)))
        return jsonify({"status": "error", "message": str(e)})

    return jsonify(data)

