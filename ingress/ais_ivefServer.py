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


connected_socket = []
disconnect_socket = []

threadFlg = True


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
    <LoginRequest Encryption="1" Name="C4ISR" Password="C4ISR_KKM"/>
    </Body>
    </MSG_IVEF>
    """

    return ivef_login    

def data_processing(xmlData, connectedSocket):
    root = ET.fromstring(xmlData)
    cnt = 0
    delItems = []

    for elem in root.iter('{http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5}ObjectDatas'):
        for ob in elem.iter('{http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5}ObjectData'):
            cnt += 1
            for id in ob.iter('{http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5}VesselData'):
                i = id.find('{http://www.iala-to-be-confirmed.org/XMLSchema/IVEF/0.2.5}Identifier').attrib

                keyList = i.keys()

                if ('MMSI' in keyList) or ('IMO' in keyList) or ('Callsign' in keyList):
                    delItems.append(ob)

        for i in delItems:
            elem.remove(i)

    filteredData = ET.tostring(root)
    filteredData = filteredData.decode().replace('ns0:', '').replace(':ns0', '')

    total_filtered = cnt - len(delItems)
    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Total Data Filtered - {str(len(delItems))}")    

    if len(connectedSocket)>0 :
        for i in connectedSocket:
            try:
                i.send(filteredData.encode('utf-8'))
                logging.info(f"[{datetime.now().astimezone().isoformat()}] : {total_filtered} Records sent.....")
            except socket.error as er:
                connected_socket.remove(i)
                disconnect_socket.append(i)


def ingress_ais_ivef():
    host = ['192.168.140.250']
    port = [8013]

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
            if time.time() - heartbeat_cur > heartbeat_cyc:
                s.close()
                s.detach()
                time.sleep(30)

                xml_data = ''
                recvData = ''

                logging.info(f'attempt to server {host[targetHost]} via port {port[targetHost]} for reconnection......')
                s = socket_connection(host[targetHost], port[targetHost], timeout)
                s.send(login_package().encode('utf-8'))

                logging.info('reconnection successed...')
                targetHost += 1
                targetHost = 0 if targetHost >= len(host) else targetHost            
                heartbeat_cur = time.time()

            recvData = s.recv(1)
            
            if len(recvData) == 0 or recvData == b'\xef' or recvData == b'\xbf' or recvData == b'\xbd':
                continue
            
            xml_data += recvData.decode()
            
            if recvData.decode() == '\n' or xml_data.strip().endswith('</MSG_IVEF>') or xml_data.strip().endswith('</MSG_IVEF>\r\n') or xml_data.strip().endswith('</MSG_IVEF>\n'):
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
                    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Total Data Received - {str(data_cnt)}")

                    t = threading.Thread(target=data_processing, args=(xml_data, connected_socket)) # create a thread object
                    t.start() # start the thread
                    xml_data = ''

                    while t.is_alive():
                        try:
                            recvData = s.recv(1)

                            if len(recvData) == 0 or recvData == b'\xef' or recvData == b'\xbf' or recvData == b'\xbd':
                                continue

                            xml_data += recvData.decode()

                            if recvData.decode() == '\n' or xml_data.endswith('</MSG_IVEF>'):
                                dict_data = xmltodict.parse(xml_data)
                                xml_data = ''

                                data_header = dict_data['MSG_IVEF']['Header']
                                data_body = dict_data['MSG_IVEF']['Body']       #['ObjectDatas']['ObjectData']

                                keys = data_body.keys()

                                logging.info(f"[{datetime.now().astimezone().isoformat()}] : {data_header}")

                                if 'Ping' in keys:
                                    heartbeat_cur = time.time()
                                    sent_heartbeats(s_socket=s, msgRefId=data_header['@MsgRefId'])
                                else:
                                    logging.info(keys)

                        except:
                            continue                            

                    logging.info(f"[{datetime.now().astimezone().isoformat()}] : {str(data_cnt)} records has been proceessed....")
                    continue   

                else:
                    logging.info(f"[{datetime.now().astimezone().isoformat()}] : {keys}")


                xml_data = ''

        except:
            # xml_data = ''
            continue
            
            


def sent_loginResponse(s_socket, msgRefId, result):
    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Received Login Request.")

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
    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Login Response Sent.")

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

    # Reserve a port for your service
    ivefServerPort = 37878

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
            # try:
            #     c, addr = s.accept()
            #     print('Got connection from', addr)

            #     c.send(b'hello')
            # except:        
            #     er = 'error'

            # # Use select to get the list of sockets ready for reading
            readable, _, _ = select.select(sockets_to_monitor, [], [])

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
                            if xml_data.strip().endswith('</MSG_IVEF>') or xml_data.strip().endswith('</MSG_IVEF>\n') or xml_data.strip().endswith('</MSG_IVEF>\r\n'):
                                dict_data = xmltodict.parse(xml_data)
                                data_header = dict_data['MSG_IVEF']['Header']
                                data_body = dict_data['MSG_IVEF']['Body']       #['ObjectDatas']['ObjectData']
                                
                                keys = data_body.keys()                                
                                logging.info(f"[{datetime.now().astimezone().isoformat()}] : {data_header}")

                                if 'LoginRequest' in keys:
                                    result = []
                                    extract_data(data_body, result)
                                    swasla = build_Swasla_Dict(result, data_header['@MsgRefId'].replace('{', '').replace('}', ''), data_header['@Version'])

                                    if swasla['Name'] == "C4ISR" and swasla['Password'] == 'C4ISR_KKM':
                                        sent_loginResponse(s_socket=sock, msgRefId=data_header['@MsgRefId'], result="1")
                                        connected_socket.append(sock)
                                    else:
                                        sent_loginResponse(s_socket=sock, msgRefId=data_header['@MsgRefId'], result="2")

                                elif 'Ping' in keys:
                                    sent_heartbeats(s_socket=sock, msgRefId=data_header['@MsgRefId'])

                                elif 'Logout' in keys:
                                    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Logout")

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
                    except:
                            sock.close()
                            sock.detach()
                            sockets_to_monitor.remove(sock)

                            if len(connected_socket) > 0:
                                connected_socket.remove(sock)                 


            if len(disconnect_socket) > 0:
                for i in disconnect_socket:
                    disconnect_socket.remove(i)
                    i.close()
                    i.detach()

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