from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from slow_control import views

urlpatterns = [
    url(r'^get_water_level', views.get_water_level, name='get_water_level'),
    url(r'^get_sc_info', views.get_sc_info, name='get_sc_info'),
    url(r'^get_sensor_newest',views.get_sensor_newest,name='get_sensor_newest'),
    url(r'^get_sensor_history',views.get_sensor_history,name='get_sensor_history'),
    url(r'^get_hv_newest', views.get_hv_newest, name='get_hv_newest'),
    url(r'^get_hv_history', views.get_hv_history,name='get_hv_history'),
    url(r'^high_voltage', login_required( TemplateView.as_view( template_name=
                                                                "slow_control/high_voltage.html"))),

    url(r'^buttonclick', views.button_click, name="button_click"),
    url(r'^button', login_required( 
        TemplateView.as_view( template_name=
                              "slow_control/button.html"))),



    url(r'$', login_required( TemplateView.as_view( template_name=
                                                    "slow_control/slow_control.html"))),                                                
    
    
]
