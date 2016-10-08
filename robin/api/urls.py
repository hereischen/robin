from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^repositories/$', views.RepoListView.as_view()),
]
