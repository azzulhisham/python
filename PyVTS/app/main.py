from crate import client
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, request
from flask_cors import cross_origin
from flask_cors import CORS
import requests
import json
import os


app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

insert_data_args = reqparse.RequestParser()
insert_data_args.add_argument("ts", type=str, help="timestamp is required", required=True)
insert_data_args.add_argument("msgtype", type=str, help="msgtype is required", required=True)
insert_data_args.add_argument("mmsi", type=str, help="mmsi is required", required=True)
insert_data_args.add_argument("sog", type=str, help="sog is required", required=True)
insert_data_args.add_argument("cog", type=str, help="cog is required", required=True)
insert_data_args.add_argument("rot", type=str, help="rot is required", required=True)
insert_data_args.add_argument("heading", type=str, help="heading is required", required=True)
insert_data_args.add_argument("lat", type=str, help="lat is required", required=True)
insert_data_args.add_argument("lng", type=str, help="lng is required", required=True)


class VTS_Gateway(Resource):
    def get(self):
        return "This is a Gateway for Mobile Navigation to the Database... V1.21"


class VTS_Insert(Resource):
    def post(self):
        req = insert_data_args.parse_args()

        url = 'https://admin:)eswlb4oW(7xjKQ3g3bv^yW&@pinc-zultan.aks1.eastus2.azure.cratedb.net:4200/_sql'

        headers = {
                    'Content-type': 'application/json', 
                }

        data = {
            "stmt": f"""insert into ais2023 (ts, msgtype, mmsi, sog, cog, rot, heading, lat, lng) values ('{req.ts}', {req.msgtype}, {req.mmsi}, {req.sog}, {req.cog}, {req.rot}, {req.heading}, {req.lat}, {req.lng});"""
        }


        resp = requests.post(url, headers=headers, json=data)
        return json.loads(resp.content), resp.status_code


@app.route("/getHistoricalData")
@cross_origin()
def getHistoricalData():
        url = 'https://admin:)eswlb4oW(7xjKQ3g3bv^yW&@pinc-zultan.aks1.eastus2.azure.cratedb.net:4200/_sql'

        print("B")
        headers = {
                    'Content-type': 'application/json', 
                }

        data = {
            "stmt": f"""select * from ais2023 where sog<>0 order by ts;"""
        }

        resp = requests.post(url, headers=headers, json=data)
        return json.loads(resp.content), resp.status_code


@app.route("/getHistoricalData/<string:startDateTime>")
@cross_origin()
def getHistoricalDataByStartDateTime(startDateTime):
        url = 'https://admin:)eswlb4oW(7xjKQ3g3bv^yW&@pinc-zultan.aks1.eastus2.azure.cratedb.net:4200/_sql'

        print("C")
        headers = {
                    'Content-type': 'application/json', 
                }

        data = {
            "stmt": f"""select * from ais2023 where ts>='{startDateTime}' and sog<>0 order by ts;"""
        }

        resp = requests.post(url, headers=headers, json=data)
        return json.loads(resp.content), resp.status_code


@app.route("/getHistoricalData/<string:mmsi>/<string:startDateTime>")
@cross_origin()
def getHistoricalDataByWhere(mmsi, startDateTime):
        url = 'https://admin:)eswlb4oW(7xjKQ3g3bv^yW&@pinc-zultan.aks1.eastus2.azure.cratedb.net:4200/_sql'

        print("D")
        headers = {
                    'Content-type': 'application/json', 
                }

        data = {
            "stmt": f"""select * from ais2023 where mmsi={mmsi} and ts>='{startDateTime}' and sog<>0 order by ts;"""
        }

        resp = requests.post(url, headers=headers, json=data)
        return json.loads(resp.content), resp.status_code
        

@app.route("/getLastPosition")
@cross_origin()
def getLastPosition():
        url = 'https://admin:)eswlb4oW(7xjKQ3g3bv^yW&@pinc-zultan.aks1.eastus2.azure.cratedb.net:4200/_sql'


        headers = {
                    'Content-type': 'application/json', 
                }

        data = {
            "stmt": f"""select * from ais2023 order by ts desc limit 1;"""
        }


        resp = requests.post(url, headers=headers, json=data)
        return json.loads(resp.content), resp.status_code


@app.route("/getLastPosition/<string:mmsi>")
@cross_origin()
def getLastPositionByWhere(mmsi):
        url = 'https://admin:)eswlb4oW(7xjKQ3g3bv^yW&@pinc-zultan.aks1.eastus2.azure.cratedb.net:4200/_sql'


        headers = {
                    'Content-type': 'application/json', 
                }

        data = {
            "stmt": f"""select * from ais2023 where mmsi={mmsi} order by ts desc limit 1;"""
        }


        resp = requests.post(url, headers=headers, json=data)
        return json.loads(resp.content), resp.status_code


api.add_resource(VTS_Gateway, "/")
api.add_resource(VTS_Insert, "/insert")
# api.add_resource(VTS_History, "/history")
# api.add_resource(VTS_LastPosition, "/lastposition")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ['py_flask_port'] if os.environ.get('py_flask_port') else 3838)