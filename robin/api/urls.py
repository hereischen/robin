from django.conf.urls import url

from . import views

# urls need to be changed later
urlpatterns = [
    url(r'^repositories/$', views.RepoListView.as_view()),
    url(r'^teams/$', views.TeamListView.as_view()),
    # url(r'^personal/$', views.PersonalStatisView.as_view()),
    url(r'^personal/$', views.personal_statistic),
    url(r'^pending/$', views.pending_patchs),
]
