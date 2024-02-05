# C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python ais_ivefServerWin.py
# to convert exe file in windows -> pyinstaller --onefile ais_ivefServerWin.py
# to run as windows service, download nssm, then setup -> nssm install <service_name> <path_to_the_exe_file> 

import socket
import select
import xmltodict
import threading
import uuid
import time
import xml.etree.ElementTree as ET
from array import *
from datetime import datetime, timezone

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

lock = threading.Lock
connected_socket = []
disconnect_socket = []

threadFlg = True


def socket_connection(host, port, timeout):
    print((host, port))
    com_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    <LoginRequest Encryption="1" Name="SWASLA_Lumut" Password="1v3f_LMT"/>
    </Body>
    </MSG_IVEF>
    """

    return ivef_login    


def sent_heartbeats(s_socket, msgRefId):
    logging.info(f"Received Ping Request.")

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
    logging.info(f"Pong Response Sent.")


def custom_thread_hook(args):
    # report the failure
    logging.info(f'[Thread failed]:: {args.exc_value}')


def data_processing(xmlData, dataCnt, connectedSocket):
    try:
        logging.info(f"Total connected client - {str(len(connectedSocket))}")

        if len(connectedSocket)>0 :
            for i in connectedSocket:   
                time.sleep(0.005)

                try:
                    with lock:
                        i.send(xmlData.encode('utf-8'))
                
                except socket.error as er:
                    logging.info(f"Socket error.....{er}")
                    connected_socket.remove(i)
                    disconnect_socket.append(i)

            logging.info(f"{dataCnt} Records sent.....")

    except:
        raise Exception('Fail to process data.......')


def ingress_ais_ivef():
    host = ['10.40.87.250']
    port = [9661]

    timeout = 120
    targetHost = 0

    logging.info(f'attempt to server {host[targetHost]} via port {port[targetHost]}......')
    s = socket_connection(host[targetHost], port[targetHost], timeout)
    s.send(login_package().encode('utf-8'))

    logging.info('connected...')
    targetHost += 1
    targetHost = 0 if targetHost >= len(host) else targetHost

    xml_data = ''
    heartbeat_cyc = timeout
    heartbeat_cur = time.time()

    while True:
        try:
            if (time.time() - heartbeat_cur > heartbeat_cyc) or s.fileno() < 0:
                s.close()
                s.detach()
                time.sleep(20)
                
                xml_data = ''
                recvData = ''

                logging.info(f'attempt to server {host[targetHost]} via port {port[targetHost]} for reconnection......')
                s = socket_connection(host[targetHost], port[targetHost], timeout)
                s.send(login_package().encode('utf-8'))

                logging.info('reconnection successed...')
                targetHost += 1
                targetHost = 0 if targetHost >= len(host) else targetHost            
                heartbeat_cur = time.time()

            recvData = s.recv(125)
            
            if len(recvData) == 0 or recvData == b'\xef' or recvData == b'\xbf' or recvData == b'\xbd':
                continue
            

            xml_data += recvData.decode()
            
            if recvData.decode() == '\n' or xml_data.strip().endswith('</MSG_IVEF>') or xml_data.strip().endswith('</MSG_IVEF>\r\n') or xml_data.strip().endswith('</MSG_IVEF>\n') or '</MSG_IVEF>' in xml_data:
                begTag = '<MSG_IVEF>'
                endTag = '</MSG_IVEF>'
                lenTag = len(endTag)
                idxTag = xml_data.find(endTag)
                
                if xml_data.count(endTag) == 1:
                    if len(xml_data) > idxTag:
                        ext_xml = xml_data[idxTag + lenTag:]
                    else:
                        ext_xml = ''
                        
                    xml_data = xml_data[0:idxTag + lenTag]
                    
                elif xml_data.count(endTag) > 1:
                    idxTag = xml_data.rfind(endTag)
                    ext_xml = xml_data[idxTag + lenTag:]
                    
                    xml_data = xml_data[xml_data.rfind(begTag):]
                    idxTag = xml_data.find(endTag)
                    xml_data = xml_data[0:idxTag + lenTag]

                
                dict_data = xmltodict.parse(xml_data)
                data_header = dict_data['MSG_IVEF']['Header']
                data_body = dict_data['MSG_IVEF']['Body']       #['ObjectDatas']['ObjectData']
                
                keys = data_body.keys()
                logging.info(f"New IVEF Package Received:: {data_header}")
            
                if 'Ping' in keys:
                    heartbeat_cur = time.time()
                    sent_heartbeats(s_socket=s, msgRefId=data_header['@MsgRefId'])

                elif 'LoginResponse' in keys:
                    heartbeat_cur = time.time()
                    logging.info(f"Login Responsed...")

                elif "ObjectDatas" in keys:
                    heartbeat_cur = time.time()
                    data_body = dict_data['MSG_IVEF']['Body']['ObjectDatas']['ObjectData']
                    data_cnt = len(data_body)
                    logging.info(f"Total Data Received - {str(data_cnt)}")

                    threading.excepthook = custom_thread_hook
                    t = threading.Thread(target=data_processing, args=(xml_data, data_cnt, connected_socket)) # create a thread object
                    t.start() # start the thread
                    xml_data = ext_xml

                    while t.is_alive():
                        try:
                            recvData = s.recv(1)
                            time.sleep(0.005)

                            if len(recvData) == 0 or recvData == b'\xef' or recvData == b'\xbf' or recvData == b'\xbd':
                                continue

                            xml_data += recvData.decode()

                            if recvData.decode() == '\n' or xml_data.endswith('</MSG_IVEF>'):
                                dict_data = xmltodict.parse(xml_data)
                                xml_data = ''

                                data_header = dict_data['MSG_IVEF']['Header']
                                data_body = dict_data['MSG_IVEF']['Body']       #['ObjectDatas']['ObjectData']

                                keys = data_body.keys()

                                logging.info(f"New IVEF Package while processing data:: {data_header}")

                                if 'Ping' in keys:
                                    heartbeat_cur = time.time()
                                    sent_heartbeats(s_socket=s, msgRefId=data_header['@MsgRefId'])
                                else:
                                    heartbeat_cur = time.time()
                                    logging.info("[Overloaded] :: " + keys)

                        except:
                            continue                           


                    logging.info(f"{str(data_cnt)} records has been proceessed....")
                    idxTag = xml_data.find(endTag)
                    
                    if endTag in xml_data:
                        if len(xml_data) > idxTag:
                            ext_xml = xml_data[idxTag + lenTag:]
                        else:
                            ext_xml = ''
                        
                        xml_data = ext_xml

                    continue   

                else:
                    logging.info(f"[Unexpected Key]:: {keys}")


                xml_data = ext_xml

        except:
            # xml_data = ''
            continue


def sent_loginResponse(s_socket, msgRefId, result):
    logging.info(f"Received Login Request.")

    refid = "{" + str(uuid.uuid4()) + "}"
    response = f"""
        <MSG_IVEF xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5">
        <Header MsgRefId="{refid}" Version="0.2.5" />
        <Body>
        <LoginResponse ResponseOn="{msgRefId}" Result="{result}" />
        </Body>
        </MSG_IVEF>    
    """

    #print(response)
    s_socket.send(response.encode('utf-8'))
    logging.info(f"Login Response Sent. Result={result}")


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


def build_Swasla_Dict(data, msgRefId, version):
  swasla_data = dict()
  swasla_data['MsgRefId'] = msgRefId
  swasla_data['Version'] = version
  
  for k, v in data:
    if not v == None:    
      swasla_data[k.replace('@', '')] =  v

  # print(swasla_data)
  return swasla_data


def main():
    # Create a socket object
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get local machine name
    ivefServer = socket.gethostname()
    ivefServer = "0.0.0.0"

    # Reserve a port for your service
    ivefServerPort = 9661

    # Bind to the port
    sc.bind((ivefServer, ivefServerPort))

    # Set the socket to non-blocking mode
    sc.setblocking(0)

    # Wait for client connection
    sc.listen(5)

    # List of sockets to be monitored by select
    sockets_to_monitor = [sc]

    print(f"Server {ivefServer} is running on port {ivefServerPort} -- v1.0")
    thread_one = threading.Thread(target=ingress_ais_ivef)
    thread_one.start()

    try:
        while True:
            logging.info(f"Total sockets to monitor = {str(len(sockets_to_monitor))}")
            
            for sockcomm in sockets_to_monitor:
                if sockcomm.fileno() < 0:
                    sockcomm.close()
                    sockcomm.detach()
                    sockets_to_monitor.remove(sockcomm)
                    logging.info(f"This remote IP is closed :: {sockcomm}")
                    
                    continue


            readable, _, _ = select.select(sockets_to_monitor, [], [], 5)
                

            for sock in readable:
                if sock is sc:
                    # A new client connection is ready to be accepted
                    c, addr = sc.accept()
                    print('Got connection from', addr)
                    sockets_to_monitor.append(c)
                    
                else:
                    try:
                        # An existing client sent data or closed the connection
                        data = sock.recv(1024)
                        xml_data = data.decode("utf-8")
                        print("data::" + xml_data)

                        if data:
                            if xml_data.strip().endswith('</MSG_IVEF>') or xml_data.strip().endswith('</MSG_IVEF>\n') or xml_data.strip().endswith('</MSG_IVEF>\r\n') or '</MSG_IVEF>' in xml_data:
                                dict_data = xmltodict.parse(xml_data)
                                data_header = dict_data['MSG_IVEF']['Header']
                                data_body = dict_data['MSG_IVEF']['Body']       #['ObjectDatas']['ObjectData']
                                
                                keys = data_body.keys()                                
                                logging.info(f"[Main thread IVEF Package]:: {data_header}")

                                if 'LoginRequest' in keys:
                                    result = []
                                    extract_data(data_body, result)
                                    swasla = build_Swasla_Dict(result, data_header['@MsgRefId'].replace('{', '').replace('}', ''), data_header['@Version'])

                                    if swasla['Name'] == "SWASLA_Enav" and swasla['Password'] == '1v3f_ENAV':
                                        sent_loginResponse(s_socket=sock, msgRefId=data_header['@MsgRefId'], result="1")
                                        connected_socket.append(sock)
                                    else:
                                        sent_loginResponse(s_socket=sock, msgRefId=data_header['@MsgRefId'], result="2")

                                elif 'Ping' in keys:
                                    sent_heartbeats(s_socket=sock, msgRefId=data_header['@MsgRefId'])

                                elif 'Logout' in keys:
                                    logging.info(f"Logout......")

                                    sock.close()
                                    sock.detach()
                                    sockets_to_monitor.remove(sock)

                                    if len(connected_socket) > 0:
                                        connected_socket.remove(sock)

                        else:
                            sock.close()
                            sock.detach()
                            sockets_to_monitor.remove(sock)

                            if len(connected_socket) > 0:
                                connected_socket.remove(sock)

                    except socket.error as e:
                            time.sleep(1)

                            sock.close()
                            sock.detach()
                            sockets_to_monitor.remove(sock)

                            if len(connected_socket) > 0:
                                connected_socket.remove(sock) 

            time.sleep(0.5)

            try:
                if len(disconnect_socket) > 0:
                    for i in disconnect_socket:
                        disconnect_socket.remove(i)
                        i.close()
                        i.detach()
            except:
                continue

    except KeyboardInterrupt:
        threadFlg = False

        if len(connected_socket) > 0:
            for i in connected_socket:
                connected_socket.remove(i)
                i.close()
                i.detach()

        thread_one.join()

        connected_socket.clear()
        disconnect_socket.clear()
        sc.close()
        sc.detach()



if __name__ == '__main__':
    main()


