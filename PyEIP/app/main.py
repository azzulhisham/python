from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, request
import requests
import xmltodict
# import pymssql
import json
import os


app = Flask(__name__)
api = Api(app)

video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("views", type=int, help="Views of the video", required=True)
video_put_args.add_argument("likes", type=int, help="Likes on the video", required=True)

videos = {}


mdm_auth_args = reqparse.RequestParser()
mdm_auth_args.add_argument("userNameOrEmailAddress", type=str, help="Username is required", required=True)
mdm_auth_args.add_argument("password", type=str, help="Password is required", required=True)
mdm_auth_args.add_argument("tenantName", type=str, help="Tenant name is required", required=True)
mdm_auth_args.add_argument("rememberClient", type=bool)

class Video(Resource):
    def get(self, id):
        if id not in videos:
            abort(404, message="Could not find video with that id")

        return videos[id]

    def put(self, id):
        args = video_put_args.parse_args()
        videos[id] = args
        return videos[id], 201


class Eip_Gateway(Resource):
    def get(self):
        return "This is a EIP Gateway for MMDIS, LRIT and DDMS."

class Lrit_ShipInfo(Resource):
    def get(self, imo):
        url = 'http://lrit.com.my/ASPPositionWebServices/service.asmx'

        headers = {
                    'Content-type': 'text/xml', 
                    'SOAPAction': 'http://LRIT.svc/GetShipInfo' 
                }

        data = f"""
            <Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
                <Body>
                    <GetShipInfo xmlns="http://LRIT.svc/">
                        <IMONumber>{imo}</IMONumber>
                    </GetShipInfo>
                </Body>
            </Envelope>
        """

        resp = requests.post(url, headers=headers, data=data)
        statusCode = resp.status_code
        result = resp.content
        data_dict = xmltodict.parse(result)

        return data_dict, statusCode


class Lrit_ShipPositions(Resource):
    def get(self):
        url = 'http://lrit.com.my/ASPPositionWebServices/service.asmx'

        #get quary string parameters
        args = request.args
        startDate = args.get("startDate")
        endDate = args.get("endDate")

        headers = {
                    'Content-type': 'text/xml', 
                    'SOAPAction': 'http://LRIT.svc/GetPositions' 
                }

        data = f"""
            <Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
                <Body>
                    <GetPositions xmlns="http://LRIT.svc/">
                        <from>{startDate}</from>
                        <to>{endDate}</to>
                    </GetPositions>
                </Body>
            </Envelope>
        """

        resp = requests.post(url, headers=headers, data=data)
        statusCode = resp.status_code
        result = resp.content
        data_dict = xmltodict.parse(result)

        return data_dict, statusCode



# class Ddms(Resource):
#     def get(self):
#         try:
#             conn = pymssql.connect(
#                 server='117.53.152.155',
#                 port=1433,
#                 user='sa',
#                 password='Enav-DB123Sql456!!!',
#                 database='VTS',
#                 as_dict=True
#             ) 

#             SQL_QUERY = f"""
#                 SELECT sl.ShipListID, 
#                 sl.IMO, 
#                 sl.CallSign, 
#                 sl.Name, 
#                 sl.ShipType, 
#                 sl.Dimension_A, 
#                 sl.Dimension_B, 
#                 sl.Dimension_C, 
#                 sl.Dimension_D, 
#                 sl.MaxDraught, 
#                 sl.Destination, 
#                 sl.ETA, 
#                 sl.EquipTypeID, 
#                 sl.ESN, 
#                 sl.DNID, 
#                 sl.MemberNumber, 
#                 ddms.* 
#                 FROM [VTS].[dbo].[ShipList] sl
#                 INNER JOIN [VTS].[dbo].[Draught] ddms on ddms.MMSI = sl.MMSI
#             """

#             cursor = conn.cursor()
#             cursor.execute(
#                 SQL_QUERY
#             )

#             records = cursor.fetchall()
#             conn.close()
            
#             for i in range(len(records)):
#                 if records[i]['ETA'] != None:
#                     records[i]['ETA'] = records[i]['ETA'].isoformat()

#                 records[i]['RecvTime'] = records[i]['RecvTime'].isoformat()

#         except (RuntimeError, TypeError, NameError):
#             print(RuntimeError)



#         return records, 200

class Mmdis_Vessel(Resource):
    def get(self, imo):
        url = 'https://mmdis.marine.gov.my/MMDIS_DIS_STG/spk/getVessel'
        
        headers = {
                    'Content-type': 'application/json', 
                }

        data = {
            "vesselId": "",
            "vesselName": "",
            "officialNumber": "",
            "imoNumber": imo
        }

        resp = requests.get(url, headers=headers, json=data)
        return json.loads(resp.text), resp.status_code


class Mdm_TokenAuth(Resource):
    def post(self):
        req = mdm_auth_args.parse_args()

        url = 'http://mdm.enav.my:50837/api/TokenAuth/Authenticate'


        headers = {
                    'Content-type': 'application/json', 
                }

        resp = requests.post(url, headers=headers, data=json.dumps(req))
        return json.loads(resp.content), resp.status_code


class Mdm_GetVessels(Resource):
    def get(self):
        #get quary string parameters
        args = request.args
        pageIndex = args.get("pageIndex")
        pageSize = args.get("pageSize")

        url = f'http://mdm.enav.my:50837/api/vessels?pageIndex={pageIndex}&pageSize={pageSize}'

        headers = {
                    'Content-type': 'application/json', 
                    'Authorization': request.headers.get('Authorization')
                }

        resp = requests.get(url, headers=headers)
        return json.loads(resp.content), resp.status_code


class Mdm_GetVesselsByCountryCode(Resource):
    def get(self, countryCode):
        #get quary string parameters
        args = request.args
        pageIndex = args.get("pageIndex")
        pageSize = args.get("pageSize")

        url = f'http://mdm.enav.my:50837/api/vesselsByCountry/{countryCode}?pageIndex={pageIndex}&pageSize={pageSize}'

        headers = {
                    'Content-type': 'application/json', 
                    'Authorization': request.headers.get('Authorization')
                }

        resp = requests.get(url, headers=headers)
        return json.loads(resp.content), resp.status_code

class Mdm_GetVesselsByMmsi(Resource):
    def get(self, mmsi):

        #get quary string parameters
        args = request.args
        startDate = args.get("startDate")
        endDate = args.get("endDate")
        pageIndex = args.get("pageIndex")
        pageSize = args.get("pageSize")

        url = f'http://mdm.enav.my:50837/api/vessels/{mmsi}?startDate={startDate}&endDate={endDate}&pageIndex={pageIndex}&pageSize={pageSize}'

        headers = {
                    'Content-type': 'application/json', 
                    'Authorization': request.headers.get('Authorization')
                }

        resp = requests.get(url, headers=headers)
        return json.loads(resp.content), resp.status_code

class Mdm_GetMethydro(Resource):
    def get(self):

        #get quary string parameters
        args = request.args
        startDate = args.get("startDate")
        endDate = args.get("endDate")
        metHydroDataType = args.get("metHydroDataType")
        pageIndex = args.get("pageIndex")
        pageSize = args.get("pageSize")

        url = f'http://mdm.enav.my:50837/api/Methydro?startDate={startDate}&endDate={endDate}&metHydroDataType={metHydroDataType}&pageIndex={pageIndex}&pageSize={pageSize}'

        headers = {
                    'Content-type': 'application/json', 
                    'Authorization': request.headers.get('Authorization')
                }

        resp = requests.get(url, headers=headers)
        return json.loads(resp.content), resp.status_code


# class Jbpi_GetEventById(Resource):
#     def get(self):
#         #get quary string parameters
#         args = request.args
#         _eventId = args.get("_eventId")

#         try:
#             conn = pymssql.connect(
#                 server='117.53.152.155',
#                 port=1433,
#                 user='sa',
#                 password='Enav-DB123Sql456!!!',
#                 database='VTS',
#                 as_dict=True
#             ) 

#             SQL_QUERY = f"""
#                 SELECT  IIF(shp.IMO is null OR shp.IMO = 0, '', CONVERT(nvarchar,shp.IMO)) as imo, IIF(shp.CallSign is null, '', CONVERT(nvarchar, shp.CallSign)) as callsign, IIF(shp.Name is null, '', CONVERT(nvarchar, shp.Name)) as vesselName,
#                 Format(evt.TimeStmp, 'dd/MM/yy HH:mm:ss') as time,
#                     CASE
#                     WHEN evt.AlarmID = 485 THEN '0' 
#                     WHEN evt.AlarmID = 486 THEN '2' 
#                     WHEN evt.AlarmID = 487 THEN '1' 
#                     WHEN evt.AlarmID = 488 THEN '7' 
#                     END as visitStatusId, 
#                     CASE
#                     WHEN evt.AlarmID = 485 THEN ''
#                     WHEN evt.AlarmID = 486 THEN ''
#                     WHEN evt.AlarmID = 487 THEN zon.ZoneName
#                     WHEN evt.AlarmID = 488 THEN zon.ZoneName
#                     END as zone 
#                 FROM Events evt 
#                 LEFT JOIN Zones zon on zon.ZoneID = evt.ZoneID 
#                 LEFT JOIN ShipList shp on shp.MMSI = evt.MMSI 
#                 WHERE EventID={_eventId} 
#             """

#             cursor = conn.cursor()
#             cursor.execute(
#                 SQL_QUERY
#             )

#             records = cursor.fetchall()
#             conn.close()
            
#         except (RuntimeError, TypeError, NameError):
#             print(RuntimeError)

#         return records, 200


#api.add_resource(Video, "/Video/<int:id>")
api.add_resource(Eip_Gateway, "/")
api.add_resource(Lrit_ShipInfo, "/lrit/shipInfo/<string:imo>")
api.add_resource(Lrit_ShipPositions, "/lrit/shipPositions")
# api.add_resource(Ddms, "/ddms/getAllVessels")
api.add_resource(Mmdis_Vessel, "/mmdis/vessel/<string:imo>")

api.add_resource(Mdm_TokenAuth, "/mdm/tokenauth/authenticate")
api.add_resource(Mdm_GetVessels, "/mdm/getvessels")
api.add_resource(Mdm_GetVesselsByCountryCode, "/mdm/getvessels/<string:countryCode>")
api.add_resource(Mdm_GetVesselsByMmsi, "/mdm/getvessel/<string:mmsi>")
api.add_resource(Mdm_GetMethydro, "/mdm/getMethydro")

# api.add_resource(Jbpi_GetEventById, "/jbpi/getEventById")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ['py_flask_port'] if os.environ.get('py_flask_port') else 3838)