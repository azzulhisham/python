import socket
import datetime
import time
from array import *


host = ['202.129.173.59', '202.129.173.60']
port = [8040, 8040]
ais_key_str = ['014e4d45415f4d444d004e4d45415f4d444d00', '014e4d45415f4d444d004e4d45415f4d444d00']

timeout = 30
targetHost = 0

while True:
    aiskey = array('b', [])
    keyLenCnt = 0
    keyHexVal = ''
    
    for n in range(int(len(ais_key_str[targetHost]))):
        keyHexVal += ais_key_str[targetHost][n:n+1]
        keyLenCnt += 1

        if keyLenCnt % 2 == 0:
            aiskey.append(int(keyHexVal, 16))
            keyHexVal = ''


    try:
        data = ''
        defaultTime = datetime.datetime(1900, 1, 1, 00, 00, 00)
        now = datetime.datetime(1900, 1, 1, 00, 00, 00)

        print(f'attempt to server {host[targetHost]} via port {port[targetHost]}...')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host[targetHost], port[targetHost]))
        s.settimeout(timeout)
        s.setblocking(0)        #set to unblocking socket operation
        s.send(aiskey)

        print('connected...')
        targetHost += 1
        targetHost = 0 if targetHost > len(host) else targetHost

        multi_package_ais = []

        while True:
            try:       
                recvData = s.recv(1)
                now = defaultTime

                if len(recvData) == 0:
                    raise Exception

                data += recvData.decode()

                if recvData.decode() == '\n':
                    if data.strip()[0:1] == '!':
                        ais_sentence = data.strip()

                        ais = ais_sentence.split(',')
                        total_package = int(ais[1])
                        package_no = int(ais[2])
                        package_id = int(ais[3]) if ais[3] else 0

                        multi_package_ais.append(ais_sentence)

                        if len(multi_package_ais) == total_package:
                            # todo :: extend the code here to send to next data processing
                            print("|".join(multi_package_ais))
                            multi_package_ais.clear()


                    data = ''

                if s.fileno() == -1:
                    break
            except:
                if now == defaultTime:
                    now = datetime.datetime.now()

                dt = datetime.datetime.now() - now
                
                if dt.total_seconds() > timeout:
                    break

                continue
        
        s.close()
        s.detach()
        print('timeout - process exited!')

        time.sleep(1)
    except:
        s.detach()

        print('network reconnection....')
        time.sleep(3)

        targetHost += 1
        targetHost = 0 if targetHost >= len(host) else targetHost

        continue

