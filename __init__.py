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
    "OxPNz49w7DOdRVcWcioG",        # shansblock       //   06/08/2026 20:40
    "hF5gbtRyCjd0oMefiAcT",        # sizanicinfo      //   07/07/2026 01:21
    "b9fSB1Mv09kwvx6ok3h3",        # sizanic          //   22/07/2026 00:11
    "20ZiA94MnqCx36ZUfOpK",        # iosShanStream    //   05/08/2026 18:06
    "pYeb4v2zvtrP1k2zZjUT",        # vPasteStream     //   12/06/2026 19:44
    "IyQcOnYy23RHbJU6XUH7"         # clyrkakenta      //   20/06/2026 20:18 (shanbox.iza)
])
last_request_time = 0

   
@app.route('/')
def hello_world():
    now = time.time()
    return "LOG du %s<br><br>%s" % (datetime.fromtimestamp(now).strftime('%d-%m-%Y %H:%M:%S'), "<br>".join(LOG))
#render_template('hello.html')

# /debrid?link=%s
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

    # plus de key disponible
    nbKeys = len(API_KEYS)
    if nbKeys == 0:
        formatted_time = datetime.fromtimestamp(now).strftime('%d-%m-%Y %H:%M:%S')
        LOG.append('%s - MAINTENANCE - %s' % (formatted_time, link))
        return jsonify({"status": "success", "data": {"link": "https://static.videezy.com/system/resources/previews/000/031/424/original/4k-work-in-progess-background-loop.mp4"}})
        #maintenanceLink = "{\r\n\"status\": \"success\",\"data\": {\"link\": \"https://m180.uqload.to/3rfkylnlsvw2q4drdixpvmpzaj7latuu54kcvhrlxt24vbgirjuu6gtblnmq/v.mp4|Referer=https://uqload.to/\"}}";
        
    time_per_key = 90 / nbKeys
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

