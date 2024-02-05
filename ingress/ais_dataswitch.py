import socket
import select
import threading
import datetime
import time
from array import *


connected_socket = []

def coroutine_one():
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

            sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sc.connect((host[targetHost], port[targetHost]))
            sc.settimeout(timeout)
            sc.setblocking(0)        #set to unblocking socket operation
            sc.send(aiskey)

            print('connected...')
            targetHost += 1
            targetHost = 0 if targetHost > len(host) else targetHost


            while True:
                try:       
                    recvData = sc.recv(1)
                    now = defaultTime

                    if len(recvData) == 0:
                        raise Exception

                    data += recvData.decode()

                    if recvData.decode() == '\n':
                        if data.strip()[0:1] == '!':
                            ais_sentence = data.strip()
                            print(ais_sentence)

                            if len(connected_socket)>0 :
                                for i in connected_socket:
                                    i.send(ais_sentence.encode('utf-8'))
                                    


                        data = ''

                    if sc.fileno() == -1:
                        break
                except:
                    if now == defaultTime:
                        now = datetime.datetime.now()

                    dt = datetime.datetime.now() - now
                    
                    if dt.total_seconds() > timeout:
                        break

                    continue
            
            sc.close()
            sc.detach()
            print('timeout - process exited!')

            time.sleep(1)
        except:
            sc.detach()

            print('network reconnection....')
            time.sleep(3)

            targetHost += 1
            targetHost = 0 if targetHost >= len(host) else targetHost

            continue



def main():

    thread_one = threading.Thread(target=coroutine_one)
    thread_one.start()

    nc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nc.connect(('0.0.0.0', 3336))
    nc.settimeout(60)
    nc.setblocking(1)        #set to unblocking socket operation
    connected_socket.append(nc)

    while True:
        test = 1
                 



if __name__ == '__main__':
    main()