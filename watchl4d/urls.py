from django.conf.urls import patterns, url, include

urlpatterns = patterns('watchl4d.website.views',
    url(r'^$', 'watchl4d'),
    url(r'^live/$', 'live'),
    url(r'^cup/$', 'cup')
)
