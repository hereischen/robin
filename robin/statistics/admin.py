from django.contrib import admin

from .models import Repository

@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'repo')
