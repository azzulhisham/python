# Import the json module
import socket
import select
import xmltodict
import json
import array
import uuid
import time
import ast
import threading

from array import *
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


connected_socket = []
disconnect_socket = []

threadFlg = True

password = "P0m4r@Apmm.gf"
escaped_password = quote_plus(password)

engine = create_engine(f'postgresql://postgres:{escaped_password}@localhost/swasla', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)



class SwaslaDto(Base):
  __tablename__ = 'swasla_dev'

  Id = Column(String, primary_key=True)
  MsgRefId = Column(String)
  Version = Column(String)

  # position & tracking data
  Altitude = Column(Float)
  EstAccAlt = Column(Float)
  EstAccLat = Column(Float)
  EstAccLong = Column(Float)
  Lat = Column(Float)
  Long = Column(Float)
  COG = Column(Float)
  EstAccSOG = Column(Float)
  EstAccCOG = Column(Float)
  Heading = Column(Float)
  ROT = Column(Float)
  SOG = Column(Float)
  UpdateTime = Column(DateTime)
  TrackStatus = Column(Integer)
  NavStatus = Column(Integer)

  # construction
  HullColor = Column(String)
  HullType = Column(Integer)
  DeadWeight = Column(Float)
  GrossWeight = Column(Float)
  Length = Column(Float)
  LloydsShipType = Column(Integer)
  YearOfBuild = Column(Integer)
  MaxAirDraught = Column(Float)
  MaxDraught = Column(Float)
  MaxPersonsOnBoard = Column(Integer)
  MaxSpeed = Column(Float)
  Width = Column(Float)

  # identifier
  Callsign = Column(String)
  IMO = Column(Integer)
  Name = Column(String)
  FormerName = Column(String)
  Flag = Column(String)
  Owner = Column(String)
  MMSI = Column(Integer)
  LRIT = Column(String)

  # vessel data
  Class = Column(Integer)
  SpecialAttention = Column(String)
  SourceId = Column(String)
  SourceName = Column(String)
  SourceType = Column(Integer)

  # waypoint
  ATA = Column(DateTime)
  ETA = Column(DateTime)
  RTA = Column(DateTime)
  LCode = Column(String)

  # voyageData
  AirDraught = Column(Float)
  CargoTypeIMO = Column(Integer)
  ContactIdentity = Column(String)
  DestCode = Column(String)
  DestName = Column(String)
  DepartCode = Column(String)
  DepartName = Column(String)
  Draught = Column(Float)
  ATD = Column(DateTime)
  ISPSLevel = Column(Float)
  OverSizedLength = Column(Float)
  OverSizedWidth = Column(Float)
  PersonsOnBoard = Column(Integer)
  Pilots = Column(Float)

  STYRIS_INFO_1 = Column(String)
  STYRIS_CREATION_U_DATE = Column(Integer)
  STYRIS_ATTENTION_LEVEL = Column(Integer)
  STYRIS_GENERIC_TYPE = Column(Integer)
  STYRIS_TYPE = Column(Integer)
  STYRIS_CANCEL_FLAG = Column(Boolean)
  STYRIS_NGL = Column(String)
  STYRIS_TRACKING_TYPE = Column(Integer)
  STYRIS_SOURCE_TYPE = Column(Integer)
  STYRIS_FREE_FLAG = Column(Boolean)
  STYRIS_CREATION_DATE = Column(Integer)
  STYRIS_AFFILIATION = Column(Integer)
  STYRIS_NAV_STATUS = Column(Integer)
  STYRIS_COMMENT = Column(String)

  def __init__(self, Id, MsgRefId, Version, Altitude='0.0', EstAccAlt='0.0', EstAccLat='0.0', Lat='0.0', Long='0.0', COG='0.0', EstAccSOG='0.0', EstAccCOG='0.0', Heading='0.0', ROT='0.0', SOG='0.0', UpdateTime=None, TrackStatus='0', NavStatus='0',
               HullColor=None, HullType='0', DeadWeight='0.0', GrossWeight='0.0', Length='0.0', LloydsShipType='0', YearOfBuild='0', MaxAirDraught='0.0', MaxDraught='0.0', MaxPersonsOnBoard='0', MaxSpeed='0.0', Width='0.0',
               Callsign=None, IMO='0', Name=None, FormerName=None, Flag=None, Owner=None, MMSI='0', LRIT=None, Class='0', SpecialAttention=None, SourceId=None, SourceName=None, SourceType='0', ATA=None, ETA=None, RTA=None, LCode=None,
               AirDraught='0.0', CargoTypeIMO='0', ContactIdentity=None, DestCode=None, DestName=None, DepartCode=None, DepartName=None, Draught='0.0', ATD=None, ISPSLevel='0.0', OverSizedLength='0.0', OverSizedWidth='0.0', PersonsOnBoard='0', Pilots='0.0',
               STYRIS_INFO_1=None, STYRIS_CREATION_U_DATE='0', STYRIS_ATTENTION_LEVEL='0', STYRIS_GENERIC_TYPE='0', STYRIS_TYPE='0', STYRIS_NGL=None, STYRIS_CANCEL_FLAG=False, STYRIS_TRACKING_TYPE='0', STYRIS_SOURCE_TYPE='0', 
               STYRIS_FREE_FLAG=False, STYRIS_CREATION_DATE='0', STYRIS_AFFILIATION='0', STYRIS_NAV_STATUS='0', STYRIS_COMMENT=None):

    self.Id = Id
    self.MsgRefId = MsgRefId
    self.Version = Version
    self.Altitude = ast.literal_eval(Altitude)
    self.EstAccAlt = ast.literal_eval(EstAccAlt)
    self.EstAccLat = ast.literal_eval(Id)
    self.EstAccLong = ast.literal_eval(EstAccLat)
    self.Lat = ast.literal_eval(Lat)
    self.Long = ast.literal_eval(Long)
    self.COG = ast.literal_eval(COG)
    self.EstAccSOG = ast.literal_eval(EstAccSOG)
    self.EstAccCOG = ast.literal_eval(EstAccCOG)
    self.Heading = ast.literal_eval(Heading)
    self.ROT = ast.literal_eval(ROT)
    self.SOG = ast.literal_eval(SOG)
    self.UpdateTime = datetime.strptime(UpdateTime, "%Y-%m-%dT%H:%M:%S.%f%z")
    self.TrackStatus = ast.literal_eval(TrackStatus)
    self.NavStatus = ast.literal_eval(NavStatus)

    self.HullColor = HullColor
    self.HullType = ast.literal_eval(HullType)
    self.DeadWeight = ast.literal_eval(DeadWeight)
    self.GrossWeight = ast.literal_eval(GrossWeight)
    self.Length = ast.literal_eval(Length)
    self.LloydsShipType = ast.literal_eval(LloydsShipType)
    self.YearOfBuild = ast.literal_eval(YearOfBuild)
    self.MaxAirDraught = ast.literal_eval(MaxAirDraught)
    self.MaxDraught = ast.literal_eval(MaxDraught)
    self.MaxPersonsOnBoard = ast.literal_eval(MaxPersonsOnBoard)
    self.MaxSpeed = ast.literal_eval(MaxSpeed)
    self.Width = ast.literal_eval(Width) 

    self.Callsign = Callsign
    self.IMO = ast.literal_eval(IMO) 
    self.Name = Name
    self.FormerName = FormerName
    self.Flag: Flag
    self.Owner = Owner
    self.MMSI = MMSI
    self.LRIT = LRIT

    self.Class = ast.literal_eval(Class) 
    self.SpecialAttention = SpecialAttention
    self.SourceId = SourceId
    self.SourceName = SourceName
    self.SourceType = ast.literal_eval(SourceType) 

    self.ATA = datetime.strptime(ATA, "%Y-%m-%dT%H:%M:%S.%f%z") if not ATA == None else None
    self.ETA = datetime.strptime(ETA, "%Y-%m-%dT%H:%M:%S.%f%z") if not ETA == None else None
    self.RTA = datetime.strptime(RTA, "%Y-%m-%dT%H:%M:%S.%f%z") if not RTA == None else None
    self.LCode = LCode

    self.AirDraught = ast.literal_eval(AirDraught) 
    self.CargoTypeIMO = ast.literal_eval(CargoTypeIMO) 
    self.ContactIdentity = ContactIdentity
    self.DestCode = DestCode
    self.DestName = DestName
    self.DepartCode = DepartCode
    self.DepartName = DepartName
    self.Draught = ast.literal_eval(Draught) 
    self.ATD = datetime.strptime(ATD, "%Y-%m-%dT%H:%M:%S.%f%z") if not ATD == None else None
    self.ISPSLevel = ast.literal_eval(ISPSLevel) 
    self.OverSizedLength = ast.literal_eval(OverSizedLength) 
    self.OverSizedWidth = ast.literal_eval(OverSizedWidth) 
    self.PersonsOnBoard = ast.literal_eval(PersonsOnBoard) 
    self.Pilots = ast.literal_eval(Pilots)   

    self.STYRIS_INFO_1 = STYRIS_INFO_1
    self.STYRIS_CREATION_U_DATE = ast.literal_eval(STYRIS_CREATION_U_DATE)
    self.STYRIS_ATTENTION_LEVEL = ast.literal_eval(STYRIS_ATTENTION_LEVEL)
    self.STYRIS_GENERIC_TYPE = ast.literal_eval(STYRIS_GENERIC_TYPE)
    self.STYRIS_TYPE = ast.literal_eval(STYRIS_TYPE)
    self.STYRIS_CANCEL_FLAG = True if STYRIS_CANCEL_FLAG == 'true' else False
    self.STYRIS_NGL = STYRIS_NGL
    self.STYRIS_TRACKING_TYPE = ast.literal_eval(STYRIS_TRACKING_TYPE)
    self.STYRIS_SOURCE_TYPE = ast.literal_eval(STYRIS_SOURCE_TYPE)
    self.STYRIS_FREE_FLAG = True if STYRIS_FREE_FLAG == 'true' else False
    self.STYRIS_CREATION_DATE = ast.literal_eval(STYRIS_CREATION_DATE)
    self.STYRIS_AFFILIATION = ast.literal_eval(STYRIS_AFFILIATION)
    self.STYRIS_NAV_STATUS = ast.literal_eval(STYRIS_NAV_STATUS)
    self.STYRIS_COMMENT = STYRIS_COMMENT


  def __repr__(self):
    return f"<SwaslaDto(Id={self.Id}, MMSI={self.MMSI}, IMO={self.IMO}, Callsign={self.Callsign})>"




# Create the table if it does not exist
Base.metadata.create_all(engine)

# Create a session and insert or update records
session = Session()




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


def build_Swasla_Dict(data, msgRefId, version):
  swasla_data = dict()
  swasla_data['MsgRefId'] = msgRefId
  swasla_data['Version'] = version
  
  for k, v in data:
    if not v == None:    
      swasla_data[k.replace('@', '')] =  v

  # print(swasla_data)
  return SwaslaDto(**swasla_data)


def get_Swasla_Dict(data, msgRefId, version):
  swasla_data = dict()
  swasla_data['MsgRefId'] = msgRefId
  swasla_data['Version'] = version

  for k, v in data:
    if not v == None:
      swasla_data[k.replace('@', '')] =  v

  # print(swasla_data)
  return swasla_data


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


def data_processing(db_session, dataBody, dataHeader):
    for i in dataBody:
        result = []
        extract_data(i, result)
        swasla = build_Swasla_Dict(result, dataHeader['@MsgRefId'].replace('{', '').replace('}', ''), dataHeader['@Version'])

        #print(swasla)
        swasla_rec = db_session.query(SwaslaDto).get(swasla.Id)
        #swasla_rec = session.query(SwaslaDto).filter(SwaslaDto.Id == swasla.Id)

        if swasla_rec is None:
            db_session.add(swasla)
        else:
            swasla_rec.Lat = swasla.Lat
            swasla_rec.Long = swasla.Long
            swasla_rec.COG = swasla.COG
            swasla_rec.Heading = swasla.Heading
            swasla_rec.ROT = swasla.ROT
            swasla_rec.SOG = swasla.SOG
            swasla_rec.UpdateTime = swasla.UpdateTime

            swasla_rec.Name = swasla.Name
            swasla_rec.MMSI = swasla.MMSI
            swasla_rec.IMO = swasla.IMO
            swasla_rec.Callsign = swasla.Callsign

            swasla_rec.SourceType = swasla.SourceType
            swasla_rec.SourceName = swasla.SourceName
            swasla_rec.TrackStatus = swasla.TrackStatus
            swasla_rec.NavStatus = swasla.NavStatus
            swasla_rec.Class = swasla.Class


    db_session.commit()


def data_filtering(xmlData, connectedSocket):
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
    logging.info(f"[{datetime.now().astimezone().isoformat()}] : Total Connected Client  - {str(len(connectedSocket))}")

    if len(connectedSocket)>0 :
        for i in connectedSocket:
            try:
                i.send(filteredData.encode('utf-8'))
                logging.info(f"[{datetime.now().astimezone().isoformat()}] : {total_filtered} Records sent.....")
            except socket.error as er:
                connected_socket.remove(i)
                disconnect_socket.append(i)


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
    recvData = ''
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

                    if isinstance(data_body, list):
                        data_cnt = len(data_body)
                        logging.info(f"[{datetime.now().astimezone().isoformat()}] : Total Data Received - {str(data_cnt)}")
                    
                        t = threading.Thread(target=data_processing, args=(session, data_body, data_header)) # create a thread object
                        t.start() # start the thread

                        x = threading.Thread(target=data_filtering, args=(xml_data, connected_socket)) # create a thread object
                        x.start() # start the thread

                        xml_data = ''

                        while t.is_alive() or x.is_alive():
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

                        logging.info(f"[{datetime.now().astimezone().isoformat()}] : {str(data_cnt)} records have been processed and committed to Db.")
                        continue                    
                    else:
                        logging.info(f"[{datetime.now().astimezone().isoformat()}] : Total Data Processed - 1")

                        result = []
                        extract_data(data_body, result)
                        swasla = build_Swasla_Dict(result, data_header['@MsgRefId'].replace('{', '').replace('}', ''), data_header['@Version'])

                        #print(swasla)
                        swasla_rec = session.query(SwaslaDto).get(swasla.Id)
                        #swasla_rec = session.query(SwaslaDto).filter(SwaslaDto.Id == swasla.Id)
                        
                        if swasla_rec is None:
                            session.add(swasla)
                        else:
                            swasla_rec.Lat = swasla.Lat
                            swasla_rec.Long = swasla.Long
                            swasla_rec.COG = swasla.COG
                            swasla_rec.Heading = swasla.Heading
                            swasla_rec.ROT = swasla.ROT
                            swasla_rec.SOG = swasla.SOG
                            swasla_rec.UpdateTime = swasla.UpdateTime

                            swasla_rec.Name = swasla.Name
                            swasla_rec.MMSI = swasla.MMSI
                            swasla_rec.IMO = swasla.IMO
                            swasla_rec.Callsign = swasla.Callsign                        

                            swasla_rec.SourceType = swasla.SourceType
                            swasla_rec.SourceName = swasla.SourceName
                            swasla_rec.TrackStatus = swasla.TrackStatus
                            swasla_rec.NavStatus = swasla.NavStatus
                            swasla_rec.Class = swasla.Class 


                        session.commit()
                else:
                    logging.info(f"[{datetime.now().astimezone().isoformat()}] : {keys}")


                xml_data = ''

        except KeyboardInterrupt:
            break

        except:
            #xml_data = ''
            continue
        
        
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

    logging.info(f"Server {ivefServer} is running on port {ivefServerPort} -- v1.0")
    thread_one = threading.Thread(target=ingress_ais_ivef)
    thread_one.start()

    try:
        while True:
            # # Use select to get the list of sockets ready for reading
            readable, _, _ = select.select(sockets_to_monitor, [], [])

            for sock in readable:
                
                if sock is sc:
                    # A new client connection is ready to be accepted
                    c, addr = sc.accept()
                    logging.info(f'Got connection from {addr[0], addr[1]}')
                    sockets_to_monitor.append(c)
                    
                else:
                    try:
                        # An existing client sent data or closed the connection
                        serverdata = sock.recv(1024)
                        xml_serverdata = serverdata.decode("utf-8")
                        logging.info("data::" + xml_serverdata)

                        if serverdata:
                            if xml_serverdata.strip().endswith('</MSG_IVEF>') or xml_serverdata.strip().endswith('</MSG_IVEF>\n') or xml_serverdata.strip().endswith('</MSG_IVEF>\r\n'):
                                dict_serverdata = xmltodict.parse(xml_serverdata)
                                serverdata_header = dict_serverdata['MSG_IVEF']['Header']
                                serverdata_body = dict_serverdata['MSG_IVEF']['Body']       #['ObjectDatas']['ObjectData']
                                
                                recvkeys = serverdata_body.keys()                                
                                logging.info(f"[{datetime.now().astimezone().isoformat()}] : Server Received IVEF package - {serverdata_header}")
                            
                                if 'LoginRequest' in recvkeys:
                                    rslt = []
                                    extract_data(serverdata_body, rslt)
                                    
                                    serverswasla = get_Swasla_Dict(rslt, serverdata_header['@MsgRefId'].replace('{', '').replace('}', ''), serverdata_header['@Version'])
                                    
                                    if serverswasla['Name'] == "SWASLA_Sabah" and serverswasla['Password'] == 'C4ISR_KKM':
                                        sent_loginResponse(s_socket=sock, msgRefId=serverdata_header['@MsgRefId'], result="1")
                                        connected_socket.append(sock)
                                    else:
                                        sent_loginResponse(s_socket=sock, msgRefId=serverdata_header['@MsgRefId'], result="2")

                                elif 'Ping' in recvkeys:
                                    sent_heartbeats(s_socket=sock, msgRefId=serverdata_header['@MsgRefId'])

                                elif 'Logout' in recvkeys:
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






