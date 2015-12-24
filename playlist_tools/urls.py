import os
from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'playlist_tools.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^$', 'pltools.views.index'),
    (r'^oauth2callback', 'pltools.views.auth_return'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login',
                           {'template_name': 'pltools/login.html'}),

    #(r'^static/(?P<path>.*)$', 'django.views.static.serve',
    #    {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),

)
