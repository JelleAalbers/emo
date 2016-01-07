from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect, HttpResponse
from pymongo import MongoClient
from django.conf import settings
from django.contrib.auth.decorators import login_required
from bson.json_util import dumps
import datetime

c = MongoClient(settings.SC_DB_ADDR)
d = c[settings.SC_DB_NAME]

@login_required
def get_sensor_newest(request):

    mongo_collection = d['slow_control']
    
    newest = mongo_collection.find_one({}, sort= [ ("_id", -1) ])
    return HttpResponse(dumps(newest), content_type="application/json")

@login_required
def get_sensor_history(request):
    
    max_points = 5000
    # include here some GET for filtering sensor/number of points    

    mongo_collection = d['slow_control']
    cursor = mongo_collection.find({}, sort= [ ("_id", -1) ], limit=max_points)

    retdoc = {}
    for doc in cursor:        
        for i in range(0, len(doc['sensors'])):
            sensor = doc['sensors'][i]
            if sensor['name'] in retdoc.keys():
                retdoc[sensor['name']].append([(doc['time']-datetime.datetime(1970,1,1))/datetime.timedelta(seconds=1)*1000, sensor['value']])
            else:
                retdoc[sensor['name']] = [[ (doc['time']-datetime.datetime(1970,1,1))/datetime.timedelta(seconds=1)*1000, sensor['value'] ]]
    return HttpResponse(dumps(retdoc), content_type="application/json")
