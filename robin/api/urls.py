from django.conf.urls import url

from . import views

# urls need to be changed later
urlpatterns = [
    url(r'^repositories/$', views.RepoListView.as_view()),
    url(r'^teams/$', views.TeamListView.as_view()),
    # url(r'^personal/$', views.PersonalStatisView.as_view()),
    url(r'^stats/opening-patchs/$', views.opening_patchs),
    url(r'^stats/closed-patchs/$', views.closed_patchs),
    url(r'^stats/updated-patchs/$', views.updated_patchs),
    url(r'^stats/commits/$', views.commit_stats),
    url(r'^stats/pending/$', views.pending_patchs),
]
