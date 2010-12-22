from django.conf.urls.defaults import *

urlpatterns = patterns('',

	(r'checkin$', 'registry.views.check', {'direction':'in'}),
        (r'checkout$', 'registry.views.check', {'direction':'out'}),

        
	#(r'resource/(?P<r_type>\w+)/(?P<r_id>\d+)/class/(?P<cim_class>\w+)/set/$', 'inventory.views.resource_class_set'),
)
