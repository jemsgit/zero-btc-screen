"""PyBluez simple example rfcomm-server.py
Simple demonstration of a server application that uses RFCOMM sockets.
Author: Albert Huang <albert@csail.mit.edu>
$Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $
"""

import bluetooth
import alarm.alarm_config as alarm_config
import conig.currency_config as currency_config

alarmConfig = alarm_config.alarmConfig

port = 1

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", port))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            # protocols=[bluetooth.OBEX_UUID]
                            )

print("Waiting for connection on RFCOMM channel", port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from", client_info)

def startSettingsServer():
  while True:
      client_sock, client_info = server_sock.accept()
      print("Accepted connection from", client_info)

      try:
          while True:
              data = client_sock.recv(1024)
              if not data:
                  break
              print("Received", data)
              client_sock.send('Ok')
      except OSError:
          pass

    print("Disconnected.")

    client_sock.close()
    server_sock.close()

def parseCommand(data):
    if(not data.startswith('req')):
        return 'false'
    else:
        req_mark, command, *params = data.split(':')
    if(command in commands):
        result = commands[command](params)
        return result
    else:
        return 'false'

def getAlarms():
    return alarmConfig.alarms

def setAlarm(*argv, currency, value, isRising):
    currency = argv[0]
    value = argv[1]
    isRising = argv[2]
    if (currency and value):
        alarmConfig.updateAlarm(currency, value, isRising)
        return 'true'
    return 'false'

def deleteAlarm(*argv):
    currency = argv[0]
    if(currency):
        alarmConfig.deleteAlarm(alarm['currency'])
        return 'true'
    return 'false'

def setUpdateUrl(*argv):
    url = argv[0]
    if(url):
        currency_config.updateCurrencyUrl(url)
        return 'true'
    return 'false'

commands = {
	'get-alarms': getAlarms,
	'set-alarm': setAlarm,
  'delete-alarm': deleteAlarm,
  'set-update-url': setUpdateUrl
}


x = threading.Thread(target=startSettingsServer)
x.start()
