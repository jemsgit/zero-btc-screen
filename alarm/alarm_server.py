from flask import Flask, jsonify, request
import alarm_config
app = Flask(__name__)

alarmConfig = alarm_config.alarmConfig

@app.route('/alarms', methods = ['GET'])
def get_alarms():
    res = jsonify(alarmConfig.alarms)
    return res

@app.route('/alarm', methods = ['POST'])
def add_alarm():
    alarm = request.json
    print(alarm.get('isRising'))
    alarmConfig.updateAlarm(alarm.get('currency'), alarm.get('value'), alarm.get('isRising'))
    return 'Ok'

@app.route('/alarm', methods = ['DELETE'])
def delete_alarm():
    alarm = request.json
    alarmConfig.deleteAlarm(alarm['currency'])
    return 'Ok'

if __name__ == '__main__':
    app.run()