from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
import os
import alarm.alarm_config as alarm_config
import config.currency_config as currency_config

alarmConfig = alarm_config.alarmConfig

app = Flask(__name__, static_folder='../web-ui/build', static_url_path='')
CORS(app)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return password == "passForCrypto"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/alarms', methods=['GET'])
@auth.login_required
def get_alarms():
    alarms = alarmConfig.alarms
    return jsonify(alarms)


@app.route('/api/alarms', methods=['POST'])
@auth.login_required
def add_alarm():
    data = request.json
    alarmConfig.updateAlarm(data['currency'], data['value'], data['isRising'], data['isActive'])
    return jsonify(alarmConfig.alarms), 201

@app.route('/api/alarms/<string:currency>', methods=['PUT'])
@auth.login_required
def update_alarm(currency):
    data = request.json
    alarmConfig.updateAlarm(currency, data['value'], data['isRising'], data['isActive'])
    return jsonify(alarmConfig.alarms)

@app.route('/api/alarms/<string:currency>', methods=['DELETE'])
@auth.login_required
def delete_alarm(currency):
    alarmConfig.deleteAlarm(currency)
    return '', 204

@app.route('/api/currency-list', methods=['GET'])
@auth.login_required
def update_currency_list_url(currency):
    listData = currency_config.currencyConfig.currencyList
    return jsonify({"list": listData})

@app.route('/api/currency-list-url', methods=['GET'])
@auth.login_required
def get_config_url():
    url = currency_config.currencyConfig.currencyUrl
    return jsonify({"url": url})

@app.route('/api/currecy-list-url', methods=['PUT'])
@auth.login_required
def update_config_url():
    data = request.json
    new_url = data.get('url')
    currency_config.currencyConfig.updateCurrencyUrl(new_url)
    # Update the config URL
    return jsonify({"url": new_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

