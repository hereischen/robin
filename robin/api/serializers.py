# -*- coding: utf-8 -*-
import logging

from rest_framework import serializers

from statistics.models import Repository, Pull, Commit, Comment
from members.models import Team, Member


logger = logging.getLogger(__name__)

STATS_TYPE = (
    (1, "Personal"),
    (2, "Team"),
)


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ('id', 'owner', 'repo')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'team_name', 'team_code')


class MemberSerializer(serializers.Serializer):
    team_code = serializers.CharField(required=True)

    class Meta:
        fields = ('team_code',)


class BasesStatsSerializer(serializers.Serializer):
    stats_type = serializers.ChoiceField(choices=STATS_TYPE, required=True)
    repository_id = serializers.IntegerField(required=True)
    team_code = serializers.CharField(required=False)
    kerbroes_id = serializers.CharField(required=False)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    class Meta:
        fields = ('repository_id', 'stats_type', 'team_code',
                  'kerbroes_id', 'query_start_date', 'query_end_date')


class CommentStatsSerializer(serializers.Serializer):
    repository_id = serializers.IntegerField(required=True)
    kerbroes_id = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    class Meta:
        fields = ('repository_id', 'kerbroes_id',
                  'query_start_date', 'query_end_date')

# class ClosedPatchSerializer(BasesStatsSerializer):
#     pass

#     class Meta(BasesStatsSerializer.Meta):
#         pass


# class OpeningPatchSerializer(serializers.Serializer):
#     stats_type = serializers.ChoiceField(choices=STATS_TYPE, required=True)
#     repository_id = serializers.IntegerField(required=True)
#     team_code = serializers.CharField(required=False)
#     kerbroes_id = serializers.CharField(required=False)
#     start_date = serializers.DateField(required=True)
#     end_date = serializers.DateField(required=True)

#     class Meta:
#         fields = ('repository_id', 'stats_type', 'team_code',
#                   'kerbroes_id', 'query_start_date', 'query_end_date')


# class CommitStatsSerializer(serializers.Serializer):
#     stats_type = serializers.ChoiceField(choices=STATS_TYPE, required=True)
#     repository_id = serializers.IntegerField(required=True)
#     team_code = serializers.CharField(required=False)
#     kerbroes_id = serializers.CharField(required=False)
#     start_date = serializers.DateField(required=True)
#     end_date = serializers.DateField(required=True)

#     class Meta:
#         fields = ('repository_id', 'stats_type', 'team_code',
#                   'kerbroes_id', 'query_start_date', 'query_end_date')


class PendingSerializer(serializers.Serializer):
    repository_id = serializers.IntegerField(required=False)

    class Meta:
        fields = ('repository_id', )

    # maybe better to remove repos!!!
    def validate(self, data):
        if not Repository.objects.is_exist(data['repository_id']):
            raise serializers.ValidationError("repository does not exist.")
        return data
