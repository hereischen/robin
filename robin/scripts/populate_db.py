from members.models import Member, Team
from statistics.models import Repository


def populate_members():
    team = Team.objects.get_or_create(team_code='x86', team_name='kvm_autotest')[0]
    print team
    Member.objects.create(kerbroes_id='hachen',
                          name='Haotong Chen',
                          github_account='hereischen',
                          team=team)
    Member.objects.create(kerbroes_id='xutian',
                          name='Xu Tian',
                          github_account='xutian',
                          team=team)

    print 'populate_members'


def populate_repos():
    Repository.objects.create(owner='hereischen', repo='robin')
    Repository.objects.create(owner='avocado-framework', repo='avocado-vt')

    print 'populate_repos'


if __name__ == '__main__':
    populate_members()
    populate_repos()
