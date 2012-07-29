'''
@author Disa Mhembere
urls patterns for one-click MR-connectome pipeline
'''

from django.conf.urls import patterns, include, url
from ocpipeline.views import hello
from ocpipeline.views import pipelineUpload
from ocpipeline.views import success
from ocpipeline.views import zipProcessedData
from ocpipeline.views import processInputData
from ocpipeline.views import confirmDownload


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ocpipeline.views',
    url(r'^$', 'default', name= 'welcome'),
    url(r'^create/$', 'hello', name= 'form-create-project'),
    url(r'^create/([a-zA-Z+#-.0-9]+/){5}$','hello', name='prog-create-project'),  # No spaces yet...
    url(r'^pipelineUpload/$', 'pipelineUpload', name='single-file-upload'),
    url(r'^pipelineUpload/(.)+$', 'pipelineUpload', name='single-file-upload'),
    url(r'^success/$', 'success', name='success-page'),
    url(r'^confirmDownload/$', 'confirmDownload', name='confirm-dwnd-page'),
    url(r'^processInput/$', 'processInputData', name='process-input-data'),
    url(r'^zipOutput/$','zipProcessedData', name = 'zip-processed-data'), # 2nd param function in view, 3rd param - anything
    # Examples
    # url(r'^$', 'myapp.views.home', name='home'),
    # url(r'^myapp/', include('myapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
