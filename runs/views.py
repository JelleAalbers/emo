from django.shortcuts import render, HttpResponse
from pymongo import MongoClient
import json
from runs.models import run_comment, run_search_form
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect
import datetime
from bson.json_util import dumps


@login_required
def runs(request):

    filter_query = {}
    # These options will be set somewhere else later?
    online_db_name = "online"
    runs_db_collection = "runs"
    mongodb_address = "localhost"
    mongodb_port = 27017

    # Connect to pymongo
    client = MongoClient(mongodb_address, mongodb_port)
    db = client[ online_db_name ]
    collection = db[ runs_db_collection ]
    fields = collection.distinct( "runmode" )
    fields.insert( 0, "All" )
    fieldslist = zip (fields, fields)

    if request.method == 'GET':
        filter_form = run_search_form( fieldslist, request.GET )

        if filter_form.is_valid():
            #build query from form
            if filter_form.cleaned_data[ 'custom' ] is not "":
                filter_query = json.loads( filter_form.cleaned_data['custom'] )
            if filter_form.cleaned_data[ 'startdate' ] is not None:
                filter_query[ 'starttimestamp' ]= { "$gt" : datetime.datetime.combine(filter_form.cleaned_data['startdate'],
                                                                        datetime.datetime.min.time() )}
            if filter_form.cleaned_data[ 'enddate' ] is not None:
                if 'starttimestamp' in filter_query.keys():
                    filter_query['starttimestamp']['$lt'] = datetime.datetime.combine(filter_form.cleaned_data['enddate'],
                                                                        datetime.datetime.max.time() )
                else:
                    filter_query[ 'starttimestamp' ]= { "$lt" : datetime.datetime.combine(filter_form.cleaned_data['enddate'],
                                                                                        datetime.datetime.max.time() )}
            if filter_form.cleaned_data[ 'mode' ] is not "" and filter_form.cleaned_data['mode'] != 'All':
                filter_query['runmode'] = filter_form.cleaned_data['mode']
    else:
        filter_form = run_search_form( fieldslist )

    retset = collection.find( filter_query ).sort( "starttimestamp", -1 )
    return render( request, 'runs/runs.html', {"runs_list": retset, "form" : filter_form } )

@login_required
def rundetail ( request ):

    # These options will have to be set somewhere else later
    online_db_name = "online"
    runs_db_collection = "runs"
    mongodb_address = "localhost"
    mongodb_port = 27017
    client = MongoClient(mongodb_address, mongodb_port)
    db = client[ online_db_name ]
    collection = db[ runs_db_collection ]
    print("HERE")
    
    
    if request.method == 'POST':
        
        # A new comment on a run
        comment = run_comment( request.POST )
        run = request.GET[ 'run' ]

        # If the comment is valid update the corresponding run
        if comment.is_valid():

            insertcomment = { "text": comment.cleaned_data['text'],
                              "date": datetime.datetime.now( datetime.timezone.utc ),
                              "user": request.user.username
                            }            
            collection.update( { "name": run },
                               { "$push": { "comments": insertcomment } },
                            )
        # Go back to the runs page
        return HttpResponsePermanentRedirect( '/runs' )
    
    # This view requires a run to be requested
    if request.method != 'GET':
        print("No get request")
        return HttpResponsePermanentRedirect( '/runs' )
    
    run = request.GET['run']
    rundoc = collection.find_one( { "name": str(run) } )
    
    # Should probably replace this with some sort of error
    if rundoc is None:
        print("Not found!")
        return HttpResponsePermanentRedirect( '/' )

    return HttpResponse( dumps(rundoc), content_type = 'application/json')


def download_list ( request ):
    
    ret = {}
    return HttpResponse( json.dumps( ret ), type = 'application/json' )
