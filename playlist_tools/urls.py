import os
from django.conf.urls import *
from django.contrib import admin
from django.views.generic.edit import CreateView
from pltools.forms import UserCreateForm

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'playlist_tools.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'pltools.views.index'),

    #tools
    url(r'^reverse', 'pltools.views.reverse', name='reverse'),
    
    #tmp
    url(r'my_videos', 'pltools.views.my_videos'),


    #auth
    url(r'^oauth2callback', 'pltools.views.auth_return'),
    url(r'^register$', CreateView.as_view(
                      template_name='pltools/register.html',
                      form_class=UserCreateForm,
                      success_url='registered'
                    ), name='register'),
    url(r'^registered$', 'pltools.views.registered'),
    url(r'login/', 'django.contrib.auth.views.login',
     {'template_name': 'pltools/login.html'}, name='login'),
    url(r'^logout$', 'pltools.views.logout_view', name='logout')

)
