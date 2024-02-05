# Import the json module
import socket
import xmltodict
import json
import array
import uuid
import time
import ast
import threading
import sys

from bs4 import BeautifulSoup
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function to recursively extract all key-value pairs from a nested dictionary
def extract_data(dictData, result):
    key = ''

    # Loop through each key-value pair in the dictionary
    for k, v in dictData.items():
        if isinstance(v, dict):
            extract_data(v, result)
        elif isinstance(v, list):
            for i in v:
              extract_data(i, result)
        else:
            if not k == '@Key' and not k == '@Value':
              result.append((k, v))
            else:
              if k == '@Key':
                key = v
              elif k == '@Value':
                if key == '':
                  key = 'NavStatus'
                result.append((key, v))


def sent_heartbeats(s_socket, msgRefId):
    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Received Ping Request.")

    refid = "{" + str(uuid.uuid4()) + "}"
    pong = f"""
        <MSG_IVEF xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5">
        <Header MsgRefId="{refid}" Version="0.2.5" />
        <Body>
        <Pong ResponseOn="{msgRefId}" TimeStamp="{datetime.now().astimezone().isoformat()}" />
        </Body>
        </MSG_IVEF>
    """

    #print(pong)
    s_socket.send(pong.encode('utf-8'))
    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Pong Response Sent.")


def socket_connection(host, port, timeout):
    com_socket = socket.socket()
    com_socket.connect((host, port))

    time.sleep(5)

    com_socket.settimeout(timeout)
    com_socket.setblocking(0)        #set to unblocking socket operation

    return com_socket


def login_package():
    refid = "{" + str(uuid.uuid4()) + "}"

    ivef_login = f"""
    <MSG_IVEF xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5">
    <Header MsgRefId="{refid}" Version="0.2.5"/>
    <Body>
    <LoginRequest Encryption="1" Name="SWASLA_Enav" Password="1v3f_ENAV"/>
    </Body>
    </MSG_IVEF>\r\n"""

    return ivef_login


def logout_package():
    refid = "{" + str(uuid.uuid4()) + "}"

    ivef_logout = f"""
    <MSG_IVEF xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5">
    <Header MsgRefId="{refid}" Version="0.2.5"/>
    <Body>
    <Logout />
    </Body>
    </MSG_IVEF>
    """

    return ivef_logout  


def log2textfile(xmldata, writeToFile=False):
    now = datetime.now()
    filename = f'swasla_{now.strftime("%Y%m%d%H")}.csv'
    soup = BeautifulSoup(xmldata, "xml")   

    if writeToFile :
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(soup.prettify() + '\n')

    print(soup.prettify() + '\n')
    

host = ['202.129.173.59']
port = [9661]

timeout = 30
targetHost = 0

logging.info(f'attempt to server {host[targetHost]} via port {port[targetHost]}......')
s = socket_connection(host[targetHost], port[targetHost], timeout)
s.send(login_package().encode('utf-8'))

logging.info('connected...')
targetHost += 1
targetHost = 0 if targetHost >= len(host) else targetHost

xml_data = ''
heartbeat_cyc = 30
heartbeat_cur = time.time()

while True:
    try:
        if s.fileno() > 0:
            recvData = s.recv(1)
        else:
            logging.info(f"Connection closed unexpectedly........ Please check your internet connection.")


        if len(recvData) == 0 or recvData == b'\xef' or recvData == b'\xbf' or recvData == b'\xbd':
            continue

        xml_data += recvData.decode()

        if recvData.decode() == '\n' or xml_data.endswith('</MSG_IVEF>'):
            dict_data = xmltodict.parse(xml_data)
            data_header = dict_data['MSG_IVEF']['Header']
            data_body = dict_data['MSG_IVEF']['Body']       #['ObjectDatas']['ObjectData']

            keys = data_body.keys()

            logging.info(f"[{datetime.now().astimezone().isoformat()}] : {data_header}")

            if 'Ping' in keys:
                heartbeat_cur = time.time()
                sent_heartbeats(s_socket=s, msgRefId=data_header['@MsgRefId'])

            elif 'LoginResponse' in keys:
                logging.info(f"[{datetime.now().astimezone().isoformat()}] : Login...")

            elif "ObjectDatas" in keys:
                data_body = dict_data['MSG_IVEF']['Body']['ObjectDatas']['ObjectData']
                data_cnt = len(data_body)
                logging.info(xml_data)
                logging.info(f"[{datetime.now().astimezone().isoformat()}] : Total Data Received - {str(data_cnt)}")

                log2textfile(xml_data)
                logging.info(f"[{datetime.now().astimezone().isoformat()}] : {str(data_cnt)} SWASLA data logged to file.")

            else:
                logging.info(f"[{datetime.now().astimezone().isoformat()}] : {keys}")


            xml_data = ''

    except KeyboardInterrupt:
        print('logout............')

        s.send(logout_package().encode('utf-8'))
        time.sleep(3)

        s.close()
        s.detach()        
        sys.exit(0)

    except:
        #xml_data = ''
        continue

