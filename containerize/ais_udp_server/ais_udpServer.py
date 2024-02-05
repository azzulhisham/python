import socket
import select
import threading
import datetime
import time
from array import *

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


connected_socket = []

threadFlg = True


def ingress_ais_sentence():
    host = ['202.129.173.59', '202.129.173.60']
    port = [8040, 8040]
    ais_key_str = ['014e4d45415f4d444d004e4d45415f4d444d00', '014e4d45415f4d444d004e4d45415f4d444d00']

    timeout = 30
    targetHost = 0

    while threadFlg:
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

            logging.info(f'attempt to server {host[targetHost]} via port {port[targetHost]}...')

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host[targetHost], port[targetHost]))
            s.settimeout(timeout)
            s.setblocking(0)        #set to unblocking socket operation
            s.send(aiskey)

            logging.info('connected...')
            targetHost += 1
            targetHost = 0 if targetHost >= len(host) else targetHost

            multi_package_ais = []

            while threadFlg:
                try:       
                    recvData = s.recv(1)
                    
                    if len(recvData) == 0:
                        raise Exception
                    else:
                        now = defaultTime

                    data += recvData.decode()

                    if recvData.decode() == '\n' :
                        if data.strip()[0:1] == '!':
                            ais_sentence = data.strip()

                            # ais = ais_sentence.split(',')
                            # total_package = int(ais[1])
                            # package_no = int(ais[2])
                            # package_id = int(ais[3]) if ais[3] else 0

                            if len(connected_socket)>0 :
                                for i in connected_socket:
                                    try:
                                        sendData = ais_sentence.split('\n')

                                        for d in sendData:
                                            if d[0:1] == '!':
                                                sc.sendto(d.encode('utf-8'), i)     
                                    except socket.error as er:
                                        logging.info("Fail to send..........................." + er)

                            logging.info(ais_sentence)

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
            logging.info('timeout - process exited!')

            time.sleep(1)
        except KeyboardInterrupt:
            s.close()
            s.detach()
            logging.info('user termination!')    

            break
        except:
            s.detach()

            logging.info('network reconnection....')
            time.sleep(3)

            targetHost += 1
            targetHost = 0 if targetHost >= len(host) else targetHost

            continue


def main():
    # Create a socket object
    global sc
    sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Get local machine name
    # host = socket.gethostname()
    host = "localhost"

    # Reserve a port for your service
    port = 10000

    logging.info(f"Server {host} is running on port {port} -- v1.0")

    connected_socket.append((host, port))
    ingress_ais_sentence()


if __name__ == '__main__':
    main()