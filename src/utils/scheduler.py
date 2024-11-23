from fnmatch import fnmatch
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger


scheduler = AsyncIOScheduler(job_defaults={'coalesce': False, 'max_instances': 100})
logger = logging.getLogger(__name__)


def remove_job_by_name_pattern(pattern: str) -> None:
    """Remove job by name pattern"""
    jobs = scheduler.get_jobs()
    for job in jobs:
        if fnmatch(job.name, pattern):
            logger.info(f'Remove job: {job.name}')
            scheduler.remove_job(job.id)
