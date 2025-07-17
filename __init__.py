from flask import Flask, jsonify, request
import requests

app = Flask(__name__)                                                                                                                  

@app.route('/')
def hello_world():
    return render_template('hello.html')


# /debrid?apikey=%s&link=%s
@app.route('/debrid')
def debrid():
    apikey = request.args.get('apikey')
    link = request.args.get('link')

    if not link or (not 'alldebrid' in link and not '1fichier' in link):
        return jsonify({"status": "error", "error": {"code": "LINK_HOST_NOT_SUPPORTED", "message": "LINK_HOST_NOT_SUPPORTED"}}), 400

#	url = "http://api.alldebrid.com/v4/link/unlock?agent=vStreamRedirect&apikey=%s&link=%s"
    url = "http://api.alldebrid.com/v4/link/unlock"
    params = {
        "agent": 'vStreamRedirect',
        "apikey": apikey,
        "link": link
    }
    
    # Envoi de la requête GET avec paramètres
    response = requests.get(url, params=params)
    data = response.json()
    return jsonify(data)

