

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from statistics.models import Repository, Pull, Commit, Comment
from members.models import Team, Member
from .serializers import (RepositorySerializer)


class RepoListView(APIView):

    """
    returns all tracked repositories
    """

    def get(self, request, format=None):
        """
        Returns a JSON response with a listing of Repository objects
        """
        repositories = Repository.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(repositories, request)
        serializer = RepositorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
