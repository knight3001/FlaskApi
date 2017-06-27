import json
import time
import requests

from flask import Flask, jsonify, request
from flask_restful import Api, Resource, abort, reqparse
from flask_cors import CORS, cross_origin

from database import insert_db, query_db

MAPURL = "https://maps.googleapis.com/maps/api/geocode/json?"
APIKEY = 'AIzaSyDdtB13gdB0BmgUvvbRe8K4_gv8n3g56aw'

app = Flask(__name__)
CORS(app)
api = Api(app)

#parser = reqparse.RequestParser()
#parser.add_argument('name', type=str)
#parser.add_argument('address', type=str)


class Job(Resource):
    def post(self):
        """
        /job
        [
            {
                "name": "AginicX",
                "address": "135 Wickham Terrace, Spring Hill QLD 4000"
            },
            {
                "name": "Espresso Garage",
                "address": "176 Grey St, South Brisbane QLD 4101"
            }
        ]
        """
        if not request.json:
            return {'error': 'not a json request'}, 400
        try:
            json_data = request.get_json(force=True)
            s = ""
            for loc in json_data:
                if not ('name' in loc and 'address' in loc):
                    return {'error': 'missing key'}, 400
                s += loc["name"] + "--" + loc["address"] + "||"

            jobid = insert_db("insert into [jobs](add_date,detail) values" +
                              "(datetime('now','localtime'), ?)", [s])
            return {"jobid": jobid, "link": "/queue/" + str(jobid)}, 202
        except Exception as e:
            return {'error': str(e)}, 400

    def get(self, jobid):
        """
        /job/1
        """
        if not jobid.isdigit():
            return {'error': 'jobid shoule be a number'}, 400

        job = query_db(
            'select * from [jobs] where job_id = ?', [jobid], one=True)
        if job is None:
            return {'error': 'jobid not matched'}, 400

        if job["complete_date"]:
            result = []
            jobList = query_db('select * from [job_location] INNER JOIN [locations] ON ' +
                               '[job_location].[location_id] = [locations].[location_id] ' +
                               'WHERE [job_location].[job_id] = ?', [jobid])
            for j in jobList:
                single = {"name": j["name"], "address": j["address"],
                          "latitude": j["latitude"], "longitude": j["longitude"]}
                result.append(single)
            return {"code": "complete", "results": result}, 200
        else:
            return {"code": "pending", "results": [jobid]}, 200


class Queue(Resource):
    def get(self, jobid):
        """
        /queue/1
        """
        if not jobid.isdigit():
            return {'error': 'jobid shoule be a number'}, 400
        job = query_db(
            'select * from [jobs] where job_id = ?', [jobid], one=True)
        if job is None:
            return {'error': 'jobid not matched'}, 400
        if job["complete_date"]:
            return {'error': 'job has completed before'}, 400

        detail = job['detail']
        for loc in detail.split("||"):
            if loc:
                locList = loc.split("--")
                location = query_db('select * from [locations] where name = ? and address = ?',
                                    [locList[0], locList[1]], one=True)
                if location is None:
                    url = MAPURL + "address=" + \
                        locList[1].replace(" ", "%") + "&key=" + APIKEY
                    response = requests.get(url)
                    data = response.json()
                    if data['status'] == 'OK':
                        geo = data['results'][0]['geometry']['location']
                        locationid = insert_db("insert into [locations]" +
                                               "(name,address,latitude,longitude) values(?,?,?,?)",
                                               [locList[0], locList[1], geo['lat'], geo['lng']])
                    else:
                        locationid = insert_db("insert into [locations]" +
                                               "(name,address,latitude,longitude) values(?,?,?,?)",
                                               [locList[0], locList[1], 0, 0])

                    insert_db("insert into [job_location](job_id, location_id) values(?, ?)",
                              [jobid, locationid])
                else:
                    insert_db("insert into [job_location](job_id, location_id) values(?, ?)",
                              [jobid, location['location_id']])
        insert_db("update [jobs] set complete_date = " +
                  "datetime('now','localtime') where job_id = ?", [jobid])
        return {"jobid": jobid, "link": "/job/" + str(jobid)}, 200


api.add_resource(Job, '/job', '/job/', '/job/<string:jobid>')
api.add_resource(Queue, '/queue/<string:jobid>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
