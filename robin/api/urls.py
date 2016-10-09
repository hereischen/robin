from django.conf.urls import url

from . import views

# urls need to be changed later
urlpatterns = [
    url(r'^repositories/$', views.RepoListView.as_view()),
    url(r'^teams/$', views.TeamListView.as_view()),
    # url(r'^personal/$', views.PersonalStatisView.as_view()),
    url(r'^stats/personal/$', views.personal_statistic),
    url(r'^stats/commits/$', views.commit_stats),
    url(r'^stats/pending/$', views.pending_patchs),
]
