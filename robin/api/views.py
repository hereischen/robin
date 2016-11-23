import logging


from datetime import datetime
from django.db.models import F
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from statistics.models import Repository, Pull, Commit, Comment
from members.models import Team, Member
from .serializers import (RepositorySerializer,
                          TeamSerializer,
                          PendingSerializer,
                          BasesStatsSerializer,
                          CommentStatsSerializer,
                          MemberSerializer,)
from commons.exceptions import APIError

logger = logging.getLogger(__name__)


def _paginate_response(data, request):
    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(data, request)
    return paginator.get_paginated_response(result_page)


def _stats_type_sortor(stats_type, team_code, kerbroes_id):
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
    return kerbroes_id_list


def _build_github_pull_url(owner, repo, pull_number):
    url = 'https://github.com/%s/%s/pull/%s' % (owner, repo, pull_number)
    return url


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
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def member_list(request):
    logger.info('[member_list] Received data : %s' % request.query_params)
    if request.method == 'GET':
        serializer = MemberSerializer(data=request.query_params)
        if serializer.is_valid():
            logger.info('[member_list] Received data is valid.')
            details = []
            team = Team.objects.get(team_code=serializer.validated_data['team_code'])
            members = Member.objects.filter(team=team)
            for member in members:
                details.append({'name': member.name,
                                'kerbroes_id': member.kerbroes_id,
                                'github_account': member.github_account,
                                })
            response = _paginate_response(details, request)
            return response

        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')


@api_view(['GET'])
def opening_patchs(request):
    logger.info('[opening_patchs] Received data : %s' % request.query_params)
    if request.method == 'GET':
        serializer = BasesStatsSerializer(data=request.query_params)
        if serializer.is_valid():
            logger.info('[opening_patchs] Received data is valid.')
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            details = []
            # repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            repo_id_list = serializer.validated_data['repository_id'].strip().split(',')
            for repo_id in repo_id_list:
                repo = Repository.objects.get(id=repo_id)
                kerbroes_id_list = _stats_type_sortor(serializer.validated_data['stats_type'],
                                                      serializer.validated_data.get('team_code', ''),
                                                      serializer.validated_data.get('kerbroes_id', ''))

                for kerbroes_id in kerbroes_id_list:
                    member = Member.objects.get(kerbroes_id=kerbroes_id)
                    pulls = Pull.objects.filter(repository=repo, author=member.github_account,
                                                created_at__range=(start_date, end_date)).order_by('created_at')
                    for pull in pulls:
                        details.append({'patch_number': pull.pull_number,
                                        'repo': repo.repo,
                                        'patch_title': pull.title,
                                        'bug_id': pull.bug_id,
                                        'author': member.kerbroes_id,
                                        'pull_merged': pull.pull_merged,
                                        'commits': pull.commits,
                                        'additions': pull.additions,
                                        'deletions': pull.deletions,
                                        'changed_files': pull.changed_files,
                                        'created_at': pull.created_at,
                                        'updated_at': pull.updated_at,
                                        'closed_at': pull.closed_at,
                                        'patch_url': _build_github_pull_url(repo.owner, repo.repo, pull.pull_number),
                                        })
            response = _paginate_response(details, request)
            return response

        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')


@api_view(['GET'])
def closed_patchs(request):
    logger.info('[closed_patchs] Received data : %s' % request.query_params)
    if request.method == 'GET':
        serializer = BasesStatsSerializer(data=request.query_params)
        if serializer.is_valid():
            logger.info('[closed_patchs] Received data is valid.')
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            details = []
            # repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            repo_id_list = serializer.validated_data['repository_id'].strip().split(',')
            for repo_id in repo_id_list:
                repo = Repository.objects.get(id=repo_id)
                kerbroes_id_list = _stats_type_sortor(serializer.validated_data['stats_type'],
                                                      serializer.validated_data.get('team_code', ''),
                                                      serializer.validated_data.get('kerbroes_id', ''))

                for kerbroes_id in kerbroes_id_list:
                    member = Member.objects.get(kerbroes_id=kerbroes_id)
                    pulls = Pull.objects.filter(repository=repo, pull_state=0, pull_merged=True,
                                                author=member.github_account,
                                                closed_at__range=(start_date, end_date))
                    for pull in pulls:
                        details.append({'patch_number': pull.pull_number,
                                        'repo': repo.repo,
                                        'patch_title': pull.title,
                                        'bug_id': pull.bug_id,
                                        'author': member.kerbroes_id,
                                        'pull_merged': pull.pull_merged,
                                        'commits': pull.commits,
                                        'additions': pull.additions,
                                        'deletions': pull.deletions,
                                        'changed_files': pull.changed_files,
                                        'created_at': pull.created_at,
                                        'updated_at': pull.updated_at,
                                        'closed_at': pull.closed_at,
                                        'patch_url': _build_github_pull_url(repo.owner, repo.repo, pull.pull_number),
                                        })
            response = _paginate_response(details, request)
            return response

        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')


@api_view(['GET'])
def updated_patchs(request):
    logger.info('[updated_patchs] Received data : %s' % request.query_params)
    if request.method == 'GET':
        serializer = BasesStatsSerializer(data=request.query_params)
        if serializer.is_valid():
            logger.info('[updated_patchs] Received data is valid.')
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            details = []
            # repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            repo_id_list = serializer.validated_data['repository_id'].strip().split(',')
            for repo_id in repo_id_list:
                repo = Repository.objects.get(id=repo_id)
                kerbroes_id_list = _stats_type_sortor(serializer.validated_data['stats_type'],
                                                      serializer.validated_data.get('team_code', ''),
                                                      serializer.validated_data.get('kerbroes_id', ''))

                for kerbroes_id in kerbroes_id_list:
                    member = Member.objects.get(kerbroes_id=kerbroes_id)
                    pulls = Pull.objects.filter(repository=repo,
                                                author=member.github_account,
                                                pull_merged=True,
                                                updated_at__range=(start_date, end_date)
                                                ).exclude(created_at=F('updated_at')
                                                         ).exclude(updated_at__gt=F('closed_at'))

                    for pull in pulls:
                        details.append({'patch_number': pull.pull_number,
                                        'repo': repo.repo,
                                        'patch_title': pull.title,
                                        'bug_id': pull.bug_id,
                                        'author': member.kerbroes_id,
                                        'pull_merged': pull.pull_merged,
                                        'commits': pull.commits,
                                        'additions': pull.additions,
                                        'deletions': pull.deletions,
                                        'changed_files': pull.changed_files,
                                        'created_at': pull.created_at,
                                        'updated_at': pull.updated_at,
                                        'closed_at': pull.closed_at,
                                        'patch_url': _build_github_pull_url(repo.owner, repo.repo, pull.pull_number),
                                        })
            response = _paginate_response(details, request)
            return response

        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')


@api_view(['GET'])
def commit_stats(request):
    logger.info('[commit_stats] Received data : %s' % request.query_params)
    if request.method == 'GET':
        serializer = BasesStatsSerializer(data=request.query_params)
        if serializer.is_valid():
            logger.info('[commit_stats] Received data is valid.')
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            details = []
            repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            kerbroes_id_list = _stats_type_sortor(serializer.validated_data['stats_type'],
                                                  serializer.validated_data.get('team_code', ''),
                                                  serializer.validated_data.get('kerbroes_id', ''))

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

            response = _paginate_response(details, request)
            return response

        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')


@api_view(['GET'])
def pending_patchs(request):
    logger.info('[pending_patchs] Received data : %s' % request.query_params)
    if request.method == 'GET':
        serializer = PendingSerializer(data=request.query_params)
        if serializer.is_valid():
            logger.info('[pending_patchs] Received data is valid.')
            details = []
            repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            pulls = Pull.objects.filter(repository=repo, pull_state=1).order_by('-created_at')
            today = datetime.today()
            for pull in pulls:
                member = Member.objects.get(github_account=pull.author)
                total_pending = today - pull.created_at
                last_updated = today - pull.updated_at
                review_comments = Comment.objects.filter(comment_type=1, pull_id=pull.id)
                details.append({'patch_number': pull.pull_number,
                                'repo': repo.repo,
                                'patch_title': pull.title,
                                'bug_id': pull.bug_id,
                                'author': member.kerbroes_id,
                                'reviews': len(review_comments),
                                'total_pending': total_pending.days,
                                'last_updated': last_updated.days,
                                'create_at': pull.created_at,
                                'updated_at': pull.updated_at,
                                'patch_url': _build_github_pull_url(repo.owner, repo.repo, pull.pull_number),
                                })

            response = _paginate_response(details, request)
            return response
        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')


@api_view(['GET'])
def comment_stats(request):
    logger.info('[comment_stats] Received data : %s' % request.query_params)
    if request.method == 'GET':
        serializer = CommentStatsSerializer(data=request.query_params)
        if serializer.is_valid():
            logger.info('[comment_stats] Received data is valid.')
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            details = []
            # repo = Repository.objects.get(id=serializer.validated_data['repository_id'])
            repo_id_list = serializer.validated_data['repository_id'].strip().split(',')
            for repo_id in repo_id_list:
                repo = Repository.objects.get(id=repo_id)
                kerbroes_id_list = serializer.validated_data.get('kerbroes_id', '').strip().split(',')
                for kerbroes_id in kerbroes_id_list:
                    member = Member.objects.get(kerbroes_id=kerbroes_id)
                    comments = Comment.objects.filter(author=member.github_account,
                                                      created_at__range=(start_date, end_date),
                                                      pull__repository=repo)
                    for comment in comments:
                        if comment.author != comment.pull.author:
                            details.append({'comment_id': comment.comment_id,
                                            'patch_number': comment.pull.pull_number,
                                            'repo': repo.repo,
                                            'author': member.kerbroes_id,
                                            'body': comment.body,
                                            'created_at': comment.created_at,
                                            'updated_at': comment.updated_at,
                                            'patch_url': _build_github_pull_url(repo.owner, repo.repo, comment.pull.pull_number),
                                            })

            response = _paginate_response(details, request)
            return response
        raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
    raise APIError(APIError.INVALID_REQUEST_METHOD, detail='Does Not Support Post Method')
