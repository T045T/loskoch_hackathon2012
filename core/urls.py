from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url('^flats/create/$', 'create_flat', name='create_flat'),
    url('^flats/join/(\w+)/$', 'join_flat', name='join_flat'),
    url('^$', 'dashboard', name='dashboard'),
    url('^vote/(\d+)/$', 'vote_for_recipe', name='vote_for_recipe'),
    url('^dashboard/schedule/', 'save_schedule', name='dashboard_save_schedule'),
    url('^facebook-connect/', 'facebook_connect'),
)
