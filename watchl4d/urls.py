from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'watchl4d.views.main'),
    url(r'^live/$', 'watchl4d.views.live'),
    url(r'^cup/$', 'watchl4d.views.cup')
)
