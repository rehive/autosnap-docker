import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv
import datetime
import time
import schedule
import logging
import iso8601

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
def create_snapshot(project, disk, zone, snapshot_name):
    logger.info('Creating Snapshot.')

    body = {'name': snapshot_name + '-' + str(int(datetime.datetime.now().timestamp()))}
    logger.info(compute.disks().createSnapshot(project=project, disk=disk, zone=zone, body=body).execute())


@catch_exceptions
def delete_old_snapshots(project, snapshot_name):
    logger.info('Deleting Old Snapshots.')

    # Get a list of all snapshots
    snapshots = compute.snapshots().list(project=project).execute()

    while ( True ) :
        next_page_token = snapshots.get("nextPageToken", None)
        for snapshot in snapshots["items"]:
            snapshot_date = iso8601.parse_date(snapshot["creationTimestamp"])
            delete_before_date = datetime.datetime.now(snapshot_date.tzinfo) - datetime.timedelta(days=7)

            # Check that a snapshot is for this disk, and that it was created
            # more than 7 days ago.
            if snapshot["name"].startswith(snapshot_name) and \
                snapshot_date < delete_before_date:
                logger.info(compute.snapshots().delete(
                    project=project, snapshot=snapshot["name"]).execute())

        if next_page_token == None:
            break

        snapshots = compute.snapshots().list(
            project=project, pageToken=next_page_token).execute()


if __name__ == '__main__':
    logger.info('Loading Google Credentials.')

    compute = build('compute', 'v1')

    if not os.environ.get('PROJECT') and os.environ.get('DISK') and os.environ.get('INTERVAL_MINUTES'):
        load_env()  # not needed if loaded via docker

    project = os.environ.get('PROJECT')
    disk = os.environ.get('DISK')
    zone = os.environ.get('ZONE')
    snapshot_name = os.environ.get('SNAPSHOT_NAME')
    interval = int(os.environ.get('INTERVAL_MINUTES'))

    # Run first snapshot:
    create_snapshot(project, disk, zone, snapshot_name)

    # Run first snapshot:
    delete_old_snapshots(project, snapshot_name)

    # Create Schedule:
    schedule.every(interval).minutes.do(create_snapshot, project, disk, zone, snapshot_name)

    # Delete old snapshots
    schedule.every(interval).minutes.do(delete_old_snapshots, project, snapshot_name)

    while True:
        schedule.run_pending()
        time.sleep(1)
