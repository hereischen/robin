from datetime import datetime, date
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from statistics.models import Repository, Pull, Commit, Comment
from members.models import Team, Member
from .serializers import (RepositorySerializer,
                          TeamSerializer,
                          PersonalStatisSerializer,
                          PendingSerializer)
from commons.exceptions import APIError


class RepoListView(APIView):
    """
    returns all tracked repositories
    """

    def get(self, request, format=None):
        # Returns a JSON response with a listing of Repository objects
        repositories = Repository.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(repositories, request)
        serializer = RepositorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TeamListView(APIView):
    """
    returns all the tracked teams
    """

    def get(self, request, format=None):
        # Returns a JSON response with a listing of Team objects
        teams = Team.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(teams, request)
        serializer = TeamSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PersonalStatisView(APIView):
    def get(self, request, format=None):
        serializer = PersonalStatisSerializer(data=request.query_params)
        if serializer.is_valid():
            print serializer.initial_data
            repository_id = serializer.initial_data['repository_id']
            kerbroes_id = serializer.initial_data['kerbroes_id']
            start_date = datetime.strptime(serializer.initial_data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(serializer.initial_data['end_date'], '%Y-%m-%d')
        raise serializer.errors
        # raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)


@api_view(['GET'])
def personal_statistic(request):
    serializer = PersonalStatisSerializer(data=request.query_params)
    if serializer.is_valid():
        repository_id = serializer.validated_data['repository_id']
        kerbroes_id = serializer.validated_data['kerbroes_id']
        start_date = datetime.strptime(serializer.validated_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(serializer.validated_data['end_date'], '%Y-%m-%d')

        repo = Repository.objects.get(id=repository_id)
        member = members.objects.get(kerbroes_id=kerbroes_id)
        # only closed pulls counts
        pulls = Pull.objects.filter(repository=repo, pull_state=0,
                                    author=member.github_account, closed_at__range=(start_date, end_date))


@api_view(['GET'])
def pending_patchs(request):
    if request.method == 'GET':
        serializer = PendingSerializer(data=request.query_params)
        if serializer.is_valid():
            detail = []
            repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            pulls = Pull.objects.filter(repository=repo, pull_state=1)
            today = datetime.today()
            for pull in pulls:
                member = Member.objects.get(github_account=pull.author)
                days = today - pull.created_at
                detail.append({'patch_number': pull.pull_number,
                               'pacth_title': pull.title,
                               'author': member.kerbroes_id,
                               'days': days.days
                               })
            return Response({'code': 0, 'msg': 'Success', 'detail': detail})
        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')
