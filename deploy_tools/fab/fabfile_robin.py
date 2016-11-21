# -*- coding: utf-8 -*-
"""Fabric远程部署脚本, TARGET_SERVER为目标部署服务器的别名, COMMAND为待执行的命令

$ fab -f yourfabfile TARGET_SERVER COMMAND

[TARGET_SERVER]
    test                测试环境
    staging             仿真环境
    prod                线上环境
    task                定时任务环境

[COMMAND]
    deploy              部署远程应用(包含应用的重启)
    health_check        检查远程服务器状态
    start_app           启动远程应用
    stop_app            停止远程应用
    restart_app         重启远程应用

    start_celery        启动远程任务队列
    stop_celery         停止远程任务队列
    restart_celery      重启远程任务队列

    update_crontab      更新定时任务
    list_crontab        显示定时任务
    remove_crontab      删除定时任务

    pull_code           更新代码至本地临时目录
    sync_code           将本地临时目录下的代码同步至远程服务器
    install_package     在远程服务器安装第三方依赖包
    database_migration  在远程服务器执行数据库迁移脚本
"""
import os
import pprint
import time
from datetime import datetime
import urllib

from fabric.api import settings, run, cd, env, prefix, hide, prompt
from fabric.colors import cyan, green, red
from fabric.contrib.project import rsync_project
from contextlib import contextmanager

DEBUG = False

PROJECT_ASCII_NAME = '''\
 _______  _______  ______  _________ _
(  ____ )(  ___  )(  ___ \ \__   __/( (    /|
| (    )|| (   ) || (   ) )   ) (   |  \  ( |
| (____)|| |   | || (__/ /    | |   |   \ | |
|     __)| |   | ||  __ (     | |   | (\ \) |
| (\ (   | |   | || (  \ \    | |   | | \   |
| ) \ \__| (___) || )___) )___) (___| )  \  |
|/   \__/(_______)|/ \___/ \_______/|/    )_)
'''
env.port = 22
env.git_branch = 'master'
env.venv_name = '.env'
env.guni_ip = '0.0.0.0'
env.guni_port = 8108
env.guni_workers = 1
env.project = 'robin'

env.project_base = '/home/hachen/projects/'
env.remote_project_base = '/home/hachen/projects/%s' % env.project
env.project_root = '/home/hachen/projects/%s' % (env.project)

env.settings = {
    'test': {
        'hosts': ['root@10.66.8.100'],
        'project_base': '/home/hachen/projects',
        'project_root': '/home/hachen/projects/%s' % env.project,
        'django_settings': 'test',
        'app_url': 'http://10.66.8.100:8108',
    },
    'staging': {
    },
    'prod': {
    },
    'task': {
    }
}


def _update_env(env_name):
    """Update environment variables."""
    env.update(env.settings[env_name])
    env.update({'target_server': env_name})
    if DEBUG:
        pprint.pprint(env)


def test():
    """Use test environment on remote host."""
    _update_env('test')


def staging():
    """Use staging environment on remote host."""
    _update_env('staging')


def prod():
    """Use prod environment on remote host."""
    _update_env('prod')


def task():
    """Use task environment on remote host."""
    _update_env('task')


@contextmanager
def _virtualenv():
    """Activate the virtual environment."""
    with cd(env.project_root):
        with prefix('source %s/bin/activate' % env.venv_name):
            yield


def _add_release_date():
    meta_file = os.path.join(env.project_root,
                             '%s/%s/__init__.py' % (env.project, env.project))
    timestamp = datetime.now().strftime('%Y%m%d %H:%M:%S')
    run("sed -i 's/^RELEASE_DATE = .*$/RELEASE_DATE = \"%s\"/' %s" %
        (timestamp, meta_file))


def pull_code():
    """Pull or clone source code from gitlib."""
    with cd(env.project_root):
        run('git reset --hard')
        run('git fetch')
        run('git pull origin %s' % env.git_branch)
        if run('git rev-parse --abbrev-ref HEAD') != env.git_branch:
            run('git checkout %s' % env.git_branch)

        _add_release_date()


def sync_code():
    """Sync source code to remote host."""
    extra_opts = '-avz'
    rsync_project(
        exclude=('.env', '.git', 'cert', 'bills',
                 'logs', 'docs', 'notes'),
        local_dir=env.project_root,
        remote_dir=env.remote_project_base,
        delete=True,
        extra_opts=extra_opts,
    )


def install_package():
    """Install third-party applications."""
    with _virtualenv():
        run('pip install -r requirements/%s.txt' % env.django_settings)


def _collect_static():
    """Collect django static files."""
    with _virtualenv():
        cmd = ('python %s/manage.py collectstatic '
               '--settings=%s.settings.%s --noinput')
        run(cmd % (env.project, env.project, env.django_settings))


def database_migration():
    """Migrate database."""
    with _virtualenv():
        cmd = ('python %s/manage.py migrate '
               '--settings=%s.settings.%s --noinput')
        run(cmd % (env.project, env.project, env.django_settings))


def stop_app():
    """Stop the application."""
    with settings(warn_only=True):
        cmd = ("ps aux|grep gunicorn|grep %s.wsgi|"
               "awk '{ print $2 }'|xargs kill -9")
        run(cmd % env.project)


def start_app():
    """Start the application."""
    with _virtualenv():
        cmd = ('gunicorn --env DJANGO_SETTINGS_MODULE=%s.settings.%s '
               '--daemon --chdir %s --workers %d --bind %s:%d %s.wsgi')
        run(cmd % (env.project, env.django_settings, env.project,
                   env.guni_workers, env.guni_ip, env.guni_port, env.project))


def restart_app():
    """Restart the application."""
    stop_app()
    start_app()


def _deploy_app_server():
    """Deploy code to application server."""
    prompt_msg = ('DEPLOY CODE TO APPLICATION SERVER %s, '
                  'PRESS ANY KEY TO CONTINUE.') % env.hosts
    prompt(green(prompt_msg))

    if env.target_server == 'test':
        # Pull code from gitlab
        pull_code()
    elif env.target_server == 'prod':
        sync_code()

    install_package()
    _collect_static()
    database_migration()

    prompt_msg = 'Press Y to restart celery and gunicorn workers(Y/N)'
    _prompt = prompt(green(prompt_msg),
                     validate=r'^(Y|N)$')
    if _prompt == 'Y':
        # restart_celery()
        restart_app()

    # Wait the process start successfully
        time.sleep(3)
        health_check()
    else:
        print red('Skip restarting celery and gunicorn workers', bold=True)


def _deploy_app_server_for_sync():
    """Deploy code to application server."""
    prompt_msg = ('DEPLOY CODE TO APPLICATION SERVER %s, '
                  'PRESS ANY KEY TO CONTINUE.') % env.hosts
    prompt(green(prompt_msg))
    if env.target_server == 'staging':
        sync_code()
        print red('New verison of codes sync to staging server.', bold=True)


def _deploy_task_server():
    """Deploy to task server."""
    prompt_msg = ('DEPLOY CODE TO TASK SERVER %s, '
                  'PRESS ANY KEY TO CONTINUE.') % env.hosts
    prompt(green(prompt_msg))

    if env.target_server == 'test':
        # Pull code from gitlab
        pull_code()
    elif env.target_server == 'task':
        sync_code()

    install_package()
    list_crontab()

    prompt_msg = 'Press Y to update cronjob(Y/N)'
    _prompt = prompt(green(prompt_msg),
                     validate=r'^(Y|N)$')
    if _prompt == 'Y':
        # Deploy source code to task server
        update_crontab()
    else:
        print red('Skip update cronjob', bold=True)


def deploy():
    """Deploy source code on remote host."""
    if env.target_server in ('test', 'prod'):
        _deploy_app_server()

    # staging only sync code
    if env.target_server == 'staging':
        _deploy_app_server_for_sync()

    if env.target_server in ('test', 'task'):
        _deploy_task_server()


def _display_process_info(cmd):
    """Display the process information on remote server."""
    awk_cmd = r'''
    awk '{ print "PROCESS ID [" $2 "] START [" $9 "]"}'
    '''
    process_info = run('|'.join((cmd, awk_cmd)))
    print process_info
    print ''


def _check_gunicorn_worker():
    """Verify gunicorn worker's count."""
    cmd = 'ps aux|grep gunicorn|grep %s|grep -v grep' % env.project
    worker_count = run('|'.join((cmd, 'wc -l')))
    print ' GUNICORN WORKERS: %s processes' % cyan(worker_count, bold=True)

    _display_process_info(cmd)


def _check_app_version():
    """Verify the application version."""
    response = urllib.urlopen(env.app_url)
    headers = response.info()
    print ' HTTP STATUS: [%s]' % cyan(response.code, bold=True)
    print ' APP VERSION: [%s]' % cyan(headers['version'], bold=True)
    print ' APP RELEASE: [%s]' % cyan(headers['release-date'], bold=True)


# def _check_celery_worker():
#     """Verify celery worker's count."""
#     cmd = 'ps aux|grep celery|grep %s|grep -v grep' % env.project
#     worker_count = run('|'.join((cmd, 'wc -l')))
#     print '   CELERY WORKERS: %s processes' % cyan(worker_count, bold=True)

#     _display_process_info(cmd)


def health_check():
    """Run health check for target server."""
    print ''
    print '/' * 80
    print green(PROJECT_ASCII_NAME, bold=True)
    print '/' * 80
    print ''
    print green('Health checking for %s %s' % (env.target_server, env.hosts),
                bold=True)
    print '+' * 80
    with settings(hide('stdout', 'stderr', 'running')):
        _check_gunicorn_worker()
        # _check_celery_worker()
        _check_app_version()


def list_crontab():
    """List all cron jobs on remove host."""
    run('crontab -l')


def remove_crontab():
    """Remove all cron jobs on remote host."""
    with settings(warn_only=True):
        run('python %s/manage.py crontab remove --settings=%s.settings.%s' %
            (env.project, env.project, env.django_settings))


def update_crontab():
    """Add cron jobs on remote host."""
    remove_crontab()

    with _virtualenv():
        run('python %s/manage.py crontab add --settings=%s.settings.%s' %
            (env.project, env.project, env.django_settings))

    list_crontab()
