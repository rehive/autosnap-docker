import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime
import time
import schedule
import logging

from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build

import functools

logger = logging.getLogger('autosnap')
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def catch_exceptions(job_func):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            job_func(*args, **kwargs)
        except:
            import traceback
            print(traceback.format_exc())
    return wrapper


def load_env():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)


@catch_exceptions
def create_snapshot(project, disk, zone):
    logger.info('Creating Snapshot.')
    body = {'name': disk + '-' + str(int(datetime.now().timestamp()))}
    logger.info(compute.disks().createSnapshot(project=project, disk=disk, zone=zone, body=body).execute())

    
@catch_exceptions
def delete_old_snapshots(project):
    logger.info('Deleting Old Snapshots.')
    # creationTimestamp
    snapshots = compute.snapshots().list(project=project).execute()
    
    for snapshot in snapshots.items:
        logger.info(compute.snapshots().delete(snapshot=snapshot.name).execute())

if __name__ == '__main__':
    print('Loading Google Credentials.')
    credentials = GoogleCredentials.get_application_default()
    compute = build('compute', 'v1', credentials=credentials)

    if not os.environ.get('PROJECT') and os.environ.get('DISK') and os.environ.get('MINUTES'):
        load_env()  # not needed if loaded via docker

    project = os.environ.get('PROJECT')
    disk = os.environ.get('DISK')
    zone = os.environ.get('ZONE')
    interval = int(os.environ.get('INTERVAL_MINUTES'))

    # Run first snapshot:
    create_snapshot(project, disk, zone)
    
    # Run first snapshot:
    delete_old_snapshots(project)

    # Create Schedule:
    schedule.every(interval).minutes.do(create_snapshot, project, disk, zone)
    
    # Delete old snapshots
    schedule.every(interval).minutes.do(delete_old_snapshots, project)

    while True:
        schedule.run_pending()
        time.sleep(1)



