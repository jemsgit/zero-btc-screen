import RPi.GPIO as GPIO
import time
import alarm.alarm_config as alarm_config

__all__ = ('alarmManager', 'AlarmManager')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
buzzer=14

GPIO.setup(buzzer,GPIO.OUT)

def checkAlarm(data, alarmValue, isRising):
    alarmValue = int(alarmValue)
    all_prices = []
    if(data == None or data[-1] == None):
        return False
    last_value = data[-1][0]
    print(last_value)
    for price in data:
      all_prices = all_prices + price
    if(len(all_prices) > 0):
      max_value = max(all_prices)
      min_value = min(all_prices)
      return ((isRising and last_value > alarmValue) or (not isRising and min_value < last_value))
    else:
      return False

class AlarmManager:
    def __init__(self):
        self.alarms = alarm_config.alarmConfig.alarms

    def alarm(self):
      GPIO.output(buzzer, GPIO.HIGH)
      time.sleep(0.05)
      GPIO.output(buzzer, GPIO.LOW)
      time.sleep(0.2)
      GPIO.output(buzzer, GPIO.HIGH)
      time.sleep(0.05)
      GPIO.output(buzzer, GPIO.LOW)
      time.sleep(0.2)
      GPIO.output(buzzer, GPIO.HIGH)
      time.sleep(0.05)
      GPIO.output(buzzer, GPIO.LOW)
    
    def checkAlarms(self, currency, data, callback):
      self.alarms = alarm_config.alarmConfig.alarms
      alarm = next((x for x in self.alarms if(x.get('currency').upper() == currency)), None)
      
      if(alarm == None):
        return False
      
      check_result = checkAlarm(data, alarm.get('value'), alarm.get('isRising'))
      if(check_result):
        alarm_config.alarmConfig.deleteAlarm(currency)
        self.alarms = alarm_config.alarmConfig.alarms
        self.alarm()
        callback(currency)


alarmManager = AlarmManager()
