from fabric.api import env, local, run, task, settings, abort, put, cd, prefix, get, sudo, shell_env, open_shell, prompt
from fabric.contrib.project import rsync_project
from dotenv import load_dotenv

import os
import logging
import posixpath


def fabric_setup():
    """ Configure Fabric
    """
    # Global config
    env.use_ssh_config = True
    env.log_level = logging.INFO


def e(file=''):
    fabric_setup()
    env.env_file = file + '.env'
    dotenv_path = os.path.join(os.path.dirname(__file__), file + '.env')

    # load env variables
    if file:
        load_dotenv(dotenv_path)
    else:
        load_dotenv(dotenv_path)

    env.project_name = os.environ.get('PROJECT_NAME', '')
    env.project_dir = posixpath.join('/srv/apps/', env.project_name)
    env.host_string = os.environ.get('HOST_NAME', '')
    env.virtual_host = os.environ.get('VIRTUAL_HOST', '')


def execute(cmd, path=''):
    # Set path:
    if not path:
        path = env.project_dir
    with cd(path):
        run(cmd)


def compose(cmd='--help', path=''):
    execute(cmd='docker-compose {cmd}'.format(cmd=cmd), path=path)


def docker(cmd='--help'):
    execute('docker {cmd}'.format(cmd=cmd))


def file_sync(cmd='get', file='.envs', use_sudo=False):
    if cmd == 'get':
        get(posixpath.join(env.project_dir, file), file)
    elif cmd == 'put':
        put(file, posixpath.join(env.project_dir, file), use_sudo=use_sudo)
        run('chmod go+r {0}'.format(posixpath.join(env.project_dir, file)))


def deploy():
    rsync_project(env.project_dir, './',
                  exclude=(
                      '.git', '.gitignore', '__pycache__', '*.pyc', '.DS_Store', 'environment.yml',
                      'fabfile.py', 'Makefile', '.idea', 'bower_components', 'node_modules', 'backups',
                      'server.env', '.env.example', 'requirements.txt', 'README.md', 'var', '.idea',
                  ),
                  delete=True)
