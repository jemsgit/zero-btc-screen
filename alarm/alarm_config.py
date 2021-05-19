import configparser
import os

__all__ = ('alarmConfig', 'AlarmConfig')


class AlarmConfig:
    def __init__(self, file_name=os.path.join(os.path.dirname(__file__), os.pardir, 'alarms.cfg')):
        self._conf = self._load_alarms(file_name)

    @property
    def alarms(self):
        alarms = list(self._conf.items('alarms'))
        alarms_list = []
        for alarm in alarms:
            alarm_cur = alarm[0]
            alarm_settings = alarm[1].split(' ')
            alarms_list.append({
              'currency': alarm_cur,
              'value': alarm_settings[0],
              'isRising': alarm_settings[1] == "True",
              'isActive': alarm_settings[2] == "True"
            })
        return alarms_list

    def updateAlarm(self, currency, value, isRising = 'False', isActive = 'True'):
        self._conf.set('alarms', currency, '%s %s %s' % (value, isRising, isActive))
        self.save_config()

    def inactivateAlarm(self, currency):
        alarm = next((x for x in self.alarms if(x.get('currency').upper() == currency)), None)
        if(alarm == None):
            return
        self._conf.set('alarms', currency, '%s %s %s' % (alarm.get('value'), alarm.get('isRising'), 'False'))
        self.save_config()


    def deleteAlarm(self, currency):
        self._conf.remove_option('alarms', currency)
        self.save_config()

    def reloadConfig(self, file_name=os.path.join(os.path.dirname(__file__), os.pardir, 'alarms.cfg')):
        self._conf = self._load_alarms(file_name)

    def save_config(self):
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'alarms.cfg'), 'w') as configfile:
            self._conf.write(configfile)

    @staticmethod
    def _load_alarms(file_name):
        conf = configparser.ConfigParser()
        conf.read_file(open(file_name))
        return conf


# we want to import the config across the files
alarmConfig = AlarmConfig()
