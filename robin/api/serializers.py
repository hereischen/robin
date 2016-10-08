# -*- coding: utf-8 -*-
import logging

from rest_framework import serializers

from statistics.models import Repository, Pull, Commit, Comment
from members.models import Team, Member


logger = logging.getLogger(__name__)


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ('pk', 'owner', 'repo')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('pk', 'team_name', 'team_code')


class PersonalStatisSerializer(serializers.Serializer):
    repository_id = serializers.IntegerField(required=True)
    kerbroes_id = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    class Meta:
        fields = ('repository_id', 'kerbroes_id', 'query_start_date', 'query_end_date')


class PendingSerializer(serializers.Serializer):
    repository_id = serializers.IntegerField(required=False)

    class Meta:
        fields = ('repository_id', )

    # maybe better to remove repos!!!
    def validate(self, data):
        if not Repository.objects.is_exist(data['repository_id']):
            raise serializers.ValidationError("repository does not exist.")
        return data
