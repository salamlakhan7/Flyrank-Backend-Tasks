import logging

from celery.signals import task_failure

logger = logging.getLogger("be06.alerts")


@task_failure.connect
def alert_on_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Fires automatically whenever any Celery task fails permanently -
    meaning it has already exhausted every retry attempt. This is the
    'someone must find out' requirement: a failed job should never just
    sit quietly in Redis waiting for a client to poll it. In a real
    production system this log line is exactly where you'd hook in
    Slack, email, or PagerDuty instead of (or alongside) stdout."""
    task_name = sender.name if sender else "unknown_task"
    logger.error(
        f"ALERT: job failed permanently after exhausting retries | "
        f"task={task_name} | task_id={task_id} | error={exception}"
    )