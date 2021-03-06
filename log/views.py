from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import datetime
import pytz
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from log.models import LogEntryForm, LogSearchForm, LogCommentForm
from bson.json_util import dumps
from django.conf import settings

def add_status(request):
    if request.method != "POST":
        return HttpResponse({}, content_type="application/json")

    new_form = LogEntryForm(request.POST)
    c = MongoClient(settings.LOG_DB_ADDR)
    d = c[settings.LOG_DB_NAME]
    mongo_collection = d['log']

    if new_form.is_valid():
        new_entry = {
            "message": new_form.cleaned_data['message'],
            "priority": 60,
            "sender": request.user.username,
            "time": pytz.utc.localize(datetime.datetime.now()),
            "run": new_form.cleaned_data['run_name'],
            "detector": new_form.cleaned_data['detector'],
            "tags": get_hash_tags(new_form.cleaned_data['message']),
        }
        mongo_collection.insert(new_entry)
    return HttpResponsePermanentRedirect("/")

def get_status(request):
    c = MongoClient(settings.LOG_DB_ADDR)
    d = c[settings.LOG_DB_NAME]
    mongo_collection = d['log']
    doc = mongo_collection.find({"priority": 60}).sort("time", -1).limit(1)[0]
    if doc is None:
        doc = {"message": "", "sender": "", "time": ""}
    return HttpResponse(dumps(doc), content_type="application/json")


def is_not_ro(user):
    if user.groups.filter(name='read_only').exists():
        return False
    return True

@login_required
def get_dispatcher_log(request):

    """
    Make the dispatcher log page
    """
    c = MongoClient(settings.LOG_DB_ADDR)
    d = c[settings.LOG_DB_NAME]

    mongo_collection = d['log']
    
    mongo_query = {"priority": {"$in": [0, 2, 3, 4, 7, 8, 9, 10]}}
    log_list = mongo_collection.find(mongo_query).sort("_id", -1)[:20]

    return HttpResponse(dumps(log_list), content_type="application/json")


@login_required
def log(request):

    """
    Make the main log page
    """
    c = MongoClient(settings.LOG_DB_ADDR)
    d = c[settings.LOG_DB_NAME]

    mongo_collection = d['log']
   
    mongo_query = {}

    # Set a default value for max entries
    max_entries = 100000

    if request.method == "GET":

        search_form = LogSearchForm(request.GET)

        if search_form.is_valid():

            # Strip the data
            if search_form.cleaned_data['custom'] != "":
                mongo_query = json.loads(search_form.cleaned_data['custom'])
            if search_form.cleaned_data['detector'] != "":
                mongo_query['detector'] = search_form.cleaned_data['detector']
            if search_form.cleaned_data['run_name'] != "":
                mongo_query['run'] = search_form.cleaned_data['run_name']
            if ( search_form.cleaned_data['priority'] == "" or 
                 search_form.cleaned_data['priority'] == -3 ):
                mongo_query['priority'] = {"$in": [0, 2, 3, 4, 7, 8, 9, 10]}
            elif search_form.cleaned_data['priority'] != '-1':

                if search_form.cleaned_data['priority'] == '-2':
                    mongo_query['priority'] = {"$gt": 1, "$lt": 5}
                else:
                    mongo_query['priority'] = int(search_form.cleaned_data['priority'])
            if search_form.cleaned_data['start_date'] is not None:
                mongo_query['date'] = {"$gt": datetime.datetime.combine(
                    search_form.cleaned_data['start_date'],
                    datetime.datetime.min.time())}
            if search_form.cleaned_data['end_date'] is not None:
                if 'date' in mongo_query.keys():
                    mongo_query['date']['$lt'] = datetime.datetime.combine(search_form.cleaned_data['end_date'],
                                                                           datetime.datetime.max.time())
                else:
                    mongo_query['time'] = {"$lt": datetime.datetime.combine(search_form.cleaned_data['end_date'],
                                                                            datetime.datetime.max.time())}
            if search_form.cleaned_data['max_entries'] is not None:
                max_entries = search_form.cleaned_data['max_entries']
    else:
        search_form = LogSearchForm()

    print(mongo_query)
    log_list = dumps(mongo_collection.find(mongo_query).sort("_id", -1)[:max_entries])

    return render(request, 'log/log.html', {"log_list": log_list, "form": search_form})


def get_hash_tags(text):
    # Takes in a text block and returns a list of hash tags
    return [tag.strip("#") for tag in text.split() if tag.startswith("#")]

@login_required
def new_comment(request):

    """
    Add a new comment to a log entry.
    """
    c = MongoClient(settings.LOG_DB_ADDR)
    d = c[settings.LOG_DB_NAME]

    mongo_collection = d['log']

    if request.method == 'POST' and is_not_ro(request.user):

        comment = LogCommentForm(request.POST)
        if comment.is_valid():
            
            # Get data
            redirect_url = comment.cleaned_data['redirect_url']
            doc_id = comment.cleaned_data['log_id']
            user = request.user.username
            date = pytz.utc.localize(datetime.datetime.now())

            # First close the issue if it's an issue closing request
            if "close_issue" in comment.cleaned_data and comment.cleaned_data['close_issue'] == True:
                mongo_collection.update({"_id": ObjectId(doc_id)}, 
                                        {"$inc": {"priority": 5},
                                         "$set": {"closed_user": user},
                                         "$set": {"closed_date": date}})

            # Now do the update to a comment if there is one
            if 'content' in comment.cleaned_data:
                text = comment.cleaned_data['content']
                user = request.user.username

                # If the entry exists append the comment to it
                comment_dict = {
                    "text": text,
                    "date": date,
                    "user":  user,
                    "tags": get_hash_tags(text),
                    "priority": 0
                    }

                mongo_collection.update({"_id": ObjectId(doc_id)}, {"$push": {"comments": comment_dict}})

            return HttpResponsePermanentRedirect(redirect_url)
    return HttpResponsePermanentRedirect('/log/')


@login_required(login_url="/login/")
def new_log_entry(request):

    redirect_url = "/log/"
    c = MongoClient(settings.LOG_DB_ADDR)
    d = c[settings.LOG_DB_NAME]

    mongo_collection = d['log']

    if request.method == 'POST' and is_not_ro(request.user):

        # Pull data from POST request form
        new_form = LogEntryForm(request.POST)

        if new_form.is_valid():
            new_entry = {
                "message": new_form.cleaned_data['message'],
                "priority": 0,
                "sender": request.user.username,
                "time": pytz.utc.localize(datetime.datetime.now()),
                "run": new_form.cleaned_data['run_name'],
                "detector": new_form.cleaned_data['detector'],
                "tags": get_hash_tags(new_form.cleaned_data['message']),
            }
            if new_form.cleaned_data['redirect'] != "":
                redirect_url = new_form.cleaned_data['redirect']

            mongo_collection.insert(new_entry)
        if redirect_url != "none":
            return HttpResponsePermanentRedirect(redirect_url)
        else:
            return HttpResponse("good")
    else:
        new_form = LogEntryForm()
    if redirect_url != 'none':
        return HttpResponsePermanentRedirect(redirect_url)
    return HttpResponse("good")

    #return render(request, 'log/newlogentry.html', {'form': new_form})

