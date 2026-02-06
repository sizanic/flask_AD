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
    #"j3652rpWbKADRK94JVkq",        # sizanic          //   25/01/2026 21:29
    "4fNx1rVZIoxgZVVfNfHe",        # sizanicinfo      //   08/02/2026 18:13
    "qFR89mjwF38ssitQsm5k",        # iosShanStream    //   09/03/2026 00:46
    "43FET5xXSC2ZsUwvC2gb",        # shansblock       //   08/02/2026 18:14
    "sBfSPtRQSbe4X4bK4D6E",        # clyrkakenta      //   04/03/2026 19:17 (shanbox.izanic)
    "sQ1eMcC27z3zUaxuHFuO"         # vPasteStream     //    10/03/2026 18:15
])
last_request_time = 0


   
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

    time_per_key = 70 / len(API_KEYS)
    if now - last_request_time < time_per_key:
        formatted_last = datetime.fromtimestamp(last_request_time).strftime('%H:%M:%S')
        last_request_time += time_per_key
        pause = last_request_time - now
        formatted_now = datetime.fromtimestamp(now).strftime('%H:%M:%S')
        formatted_new = datetime.fromtimestamp(last_request_time).strftime('%H:%M:%S')

        # pause trop longue, on fait patienter quelques secondes mais on refuse
        if pause > 10:
            last_request_time -= time_per_key
            smallPause = 8
            LOG.append('last %s - now %s - new %s - sleep %d ----  TIME_OUT' % (formatted_last, formatted_now, formatted_new, smallPause))
            time.sleep(smallPause)
            return jsonify({"status": "error", "error": {"code": "TIME_OUT", "message": "DELAI DEPASSE, RETENTEZ"}})

        LOG.append('last %s - now %s - new %s - sleep %d' % (formatted_last, formatted_now, formatted_new, pause))
        time.sleep(pause)
        now = time.time()
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
            last_request_time = 0  # pas besoin d'attendre pour tester la clé suivante
            return debrid()  # réessaie avec une autre clé
        API_KEYS.append(apikey)    # on replace la key à la fin car elle est toujours valide
        data = response.json()
    except Exception as e:
        API_KEYS.append(apikey)
        formatted_time = datetime.fromtimestamp(now).strftime('%d-%m-%Y %H:%M:%S')
        LOG.append('%s -> %s' % (formatted_time, str(e)))
        return jsonify({"status": "error", "message": str(e)})

    return jsonify(data)

