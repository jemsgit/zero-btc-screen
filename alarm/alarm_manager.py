# import RPi.GPIO as GPIO
import alarm_config

# GPIO.setmode(GPIO.BCM)

__all__ = ('alarmManager', 'AlarmManager')

# GPIO.setmode(GPIO.BCM)

# #GPIO.output(buzzer,GPIO.HIGH)
# #GPIO.output(buzzer,GPIO.LOW)

def checkAlarm(data, alarmValue, isRising):
    print("Check")

class AlarmManager:
    def __init__(self):
        #GPIO.setup(BUZZER,GPIO.OUT)
        self.alarms = alarm_config.alarms
    
    def checkAlarms(self, currency, data, callback):
      alarm = next(x for x in self.alarms if(x.get('currency').upper() == currency))
      if(alarm == None) {
        return;
      }
      checkAlarm(data, alarm.get('value'), alarm.get('isRising'))

alarmManager = AlarmManager()
