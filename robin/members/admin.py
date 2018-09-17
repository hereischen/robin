from django.contrib import admin

from .models import Team, Member


class MemberInline(admin.StackedInline):
    model = Member


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'team_code', 'number_of_active_members')
    readonly_fields = ( 'number_of_active_members',)
    inlines = [
        MemberInline,
    ]

    def number_of_active_members(self, obj):
        return len(Member.objects.filter(team_id=obj.id, serving=True))


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'kerbroes_id',
                    'serving',
                    'leave_date',
                    'team')
    empty_value_display = 'unknown'

    def team(self, obj):
        return Team.objects.get(id=obj.team_id).name
