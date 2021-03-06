from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from runs import views
urlpatterns = [

    url(r'^newtag',views.addTag,name='newtag'),
    url(r'^newcomment', views.new_comment, name='newcomment'),
    url(r'^download_list',views.download_list,name='download_list'),
    url(r'^last_run_per_det', views.last_run_per_det, name="last_run_per_det"),
    url(r'^runs_started', views.runs_started, name="runs_started"),
    url(r'^get_run', views.get_run, name="get_run"),
    url(r'^runs_stream', views.runs_stream, name="runs_stream"),
    url(r'^old', login_required( views.runs ), name='runs' ),
    url(r'^processing', login_required(TemplateView.as_view
                                       (template_name='runs/whatdata.html'))),
    url(r'^get_processing_progress', views.get_processing_progress, 
        name='get_processing_progress'),
    url(r'^get_current_exposure', views.get_current_exposure,
        name='get_current_exposure'),
    url(r'^get_exposure_text', views.get_exposure_text, 
        name='get_exposure_text'),
    #url(r'^getpaxreport', views.get_pax_report, name='get_pax_report'),
    url(r'^wheres_the_data', views.wheres_the_data, name='wheres_the_data'), 
    url(r'$', login_required(TemplateView.as_view
                                (template_name="runs/runs_new.html"))),
]

