from django.conf.urls import patterns, url

urlpatterns = patterns('recipes.views',
    url('^create/$', 'add_recipe', name='add_recipe')
)
