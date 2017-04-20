import os
import csv
from members.models import Member, Team
from statistics.models import Repository

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print os.path.join(ROOT_DIR, 'team_member_data.csv')


def populate_members():
    with open(os.path.join(ROOT_DIR, 'team_member_data.csv')) as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0
        for row in reader:
            if row['Github_Account'] != '':
                counter += 1
                print(row['Github_Account'], row['Name'], row['Kerberos'], row['Team_Code'])
                team = Team.objects.get_or_create(team_code=row['Team_Code'], team_name=row['Team_Code'])[0]
                member = Member.objects.create(kerbroes_id=row['Kerberos'],
                                               name=row['Name'],
                                               github_account=row['Github_Account'],
                                               team=team)
                print member
        print counter
    print 'populate_members done'


def populate_repos():
    Repository.objects.create(owner='avocado-framework', repo='avocado-vt')
    Repository.objects.create(owner='avocado-framework', repo='avocado')
    Repository.objects.create(owner='autotest', repo='tp-qemu')
    Repository.objects.create(owner='autotest', repo='autotest-client-tests')
    repos = Repository.objects.all()

    print '%s repos are created' % len(repos)
    print repos


def populate_db():
    populate_members()
    populate_repos()


if __name__ == '__main__':
    populate_members()
    populate_repos()
