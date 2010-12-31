from settings import MEDIA_ROOT
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import admindocs
admin.autodiscover()

urlpatterns = patterns('',
        (r'^admin/doc/', include(admindocs.urls)),
    	(r'^admin/',  include(admin.site.urls)),

	(r'^registry/', include('registry.urls')),
)
