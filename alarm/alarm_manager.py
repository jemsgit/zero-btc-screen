import RPi.GPIO as GPIO
import time
import threading
import alarm.alarm_config as alarm_config

__all__ = ('alarmManager', 'AlarmManager')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
buzzer=14

GPIO.setup(buzzer,GPIO.OUT)

def checkAlarm(last_value, alarmValue, isRising):
    alarmValue = int(alarmValue)
    if(last_value == None):
        return False
    print('checkAlarm')
    print(last_value)
    return ((isRising and last_value > alarmValue) or (not isRising and alarmValue > last_value))

class AlarmManager:
    def __init__(self):
        self.alarms = alarm_config.alarmConfig.alarms
        alarm_config.alarmConfig.subsribe(self.reinit)
        self.isAlarm = False

    def reinit(self):
        self.alarms = alarm_config.alarmConfig.alarms
        self.isAlarm = False

    def stopAlarm(self):
      self.isAlarm = False

    def alarmRing(self):
      while self.isAlarm:
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(0.2)

    def alarm(self):
      x = threading.Thread(target=self.alarmRing)
      x.start()
    
    def checkAlarms(self, currency, data, callback):
      self.alarms = alarm_config.alarmConfig.alarms
      alarm = next((x for x in self.alarms if(x.get('currency').upper() == currency)), None)
      if(alarm == None or alarm.get('isActive') == False):
        return False
      
      check_result = checkAlarm(data, alarm.get('value'), alarm.get('isRising'))
      if(check_result):
        alarm_config.alarmConfig.inactivateAlarm(currency)
        self.alarms = alarm_config.alarmConfig.alarms
        self.isAlarm = True
        self.alarm()
        callback(currency)


alarmManager = AlarmManager()
