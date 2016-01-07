from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from slow_control import views

urlpatterns = [
    url(r'^get_sensor_newest',views.get_sensor_newest,name='get_sensor_newest'),
    url(r'^get_sensor_history',views.get_sensor_history,name='get_sensor_history'),
    url(r'$', login_required( TemplateView.as_view( template_name=
                                                    "slow_control/slow_control.html"))),                                                

]
