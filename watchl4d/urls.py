from django.conf.urls import patterns, url, include
from django.contrib import admin
import watchl4d.website.admin

urlpatterns = patterns('watchl4d.website.views',
    url(r'^$', 'watchl4d'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^register/$', 'register'),
    url(r'^deleteteam/$', 'deleteteam'),
    url(r'^team/$', 'team'),
    url(r'^live/$', 'live'),
    url(r'^cup/$', 'cup'),

    url(r'^admin/', include(admin.site.urls))
)
