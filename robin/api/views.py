from datetime import datetime, date
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from statistics.models import Repository, Pull, Commit, Comment
from members.models import Team, Member
from .serializers import (RepositorySerializer,
                          TeamSerializer,
                          PersonalStatsSerializer,
                          PendingSerializer,
                          CommitStatsSerializer)
from commons.exceptions import APIError


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


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
        print serializer.data
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
    serializer = PersonalStatsSerializer(data=request.query_params)
    if serializer.is_valid():
        repository_id = serializer.validated_data['repository_id']
        kerbroes_id = serializer.validated_data['kerbroes_id']
        start_date = datetime.strptime(serializer.validated_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(serializer.validated_data['end_date'], '%Y-%m-%d')

        repo = Repository.objects.get(id=repository_id)
        member = members.objects.get(kerbroes_id=kerbroes_id)
        pulls = Pull.objects.filter(repository=repo, pull_state=0,
                                    author=member.github_account, closed_at__range=(start_date, end_date))


@api_view(['GET'])
def commit_stats(request):
    if request.method == 'GET':
        serializer = CommitStatsSerializer(data=request.query_params)
        if serializer.is_valid():
            stats_type = serializer.validated_data['stats_type']
            repository_id = serializer.validated_data['repository_id']
            team_code = serializer.validated_data.get('team_code', '')
            kerbroes_id = serializer.validated_data.get('kerbroes_id', '')
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            details = []
            repo = Repository.objects.get(id=repository_id)
            if stats_type == 1:
                # personal stats_type = 1, does not need team code
                # personal takes a string of kerbroes_id, seperated with ',''
                kerbroes_id_list = kerbroes_id.strip().split(',')
            elif stats_type == 2:
                # team stats_type = 2, does not need kerbroes_id
                # team  takes a team_code
                team = Team.objects.get(team_code=team_code)
                members = Member.objects.filter(team=team)
                kerbroes_id_list = [member.kerbroes_id for member in members]

            for kerbroes_id in kerbroes_id_list:
                member = Member.objects.get(kerbroes_id=kerbroes_id)
                commits = Commit.objects.filter(repository=repo, email=member.rh_email,
                                                date__range=(start_date, end_date))
                for commit in commits:
                    details.append({'sha': commit.sha[:8],
                                    'author': member.kerbroes_id,
                                    'message': commit.message,
                                    'date': commit.date,
                                    'patch_number': commit.pull.pull_number
                                    })

            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(details, request)
            response = paginator.get_paginated_response(result_page)
            return response

        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')


@api_view(['GET'])
def pending_patchs(request):
    if request.method == 'GET':
        serializer = PendingSerializer(data=request.query_params)
        if serializer.is_valid():
            details = []
            repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            pulls = Pull.objects.filter(repository=repo, pull_state=1)
            today = datetime.today()
            for pull in pulls:
                member = Member.objects.get(github_account=pull.author)
                total_pending = today - pull.created_at
                last_updated = today - pull.updated_at
                details.append({'patch_number': pull.pull_number,
                                'pacth_title': pull.title,
                                'author': member.kerbroes_id,
                                'total_pending': total_pending.days,
                                'last_updated': last_updated.days,
                                })
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(details, request)
            response = paginator.get_paginated_response(result_page)
            return response
        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')
