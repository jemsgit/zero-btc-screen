import configparser
import os
import RPi.GPIO as GPIO
from http.server import HTTPServer, BaseHTTPRequestHandler
import simplejson

GPIO.setmode(GPIO.BCM)

__all__ = ('alarm', 'Alarm')

BUZZER=23
PORT = 8082
SERVER_ADDERESS = "localhost"
GPIO.setmode(GPIO.BCM)

#GPIO.output(buzzer,GPIO.HIGH)
#GPIO.output(buzzer,GPIO.LOW)

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        print("in post method")
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(200)
        self.end_headers()

        data = simplejson.loads(self.data_string)
        print("{}".format(data))
        f = open("for_presen.py")
        self.wfile.write(f.read())
        return

def start_server():
    server_address = (SERVER_ADDERESS, PORT)
    httpd = HTTPServer(server_address, S)

    print(f"Starting httpd server on {SERVER_ADDERESS}:{PORT}")
    httpd.serve_forever()

class Alarm:
    def __init__(self, file_name=os.path.join(os.path.dirname(__file__), os.pardir, 'alarms.cfg')):
        GPIO.setup(BUZZER,GPIO.OUT)
        self._conf = self._load_alarms_cofig(file_name)
        self._set_config_server()

    @staticmethod
    def _set_config_server():
        start_server()

    @staticmethod
    def _set_alarms(file_name):
        start_server()

    @staticmethod
    def _load_alarms_cofig(file_name):
        conf = configparser.ConfigParser()
        conf.read_file(open(file_name))
        return conf
        

alarm = Alarm()
