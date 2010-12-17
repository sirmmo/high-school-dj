from django.conf.urls.defaults import *

urlpatterns = patterns('',

	(r'checkin$', 'registry.views.check.cin'),
        (r'checkout$', 'registry.views.check.cout'),

        
	#(r'resource/(?P<r_type>\w+)/(?P<r_id>\d+)/class/(?P<cim_class>\w+)/set/$', 'inventory.views.resource_class_set'),
)
