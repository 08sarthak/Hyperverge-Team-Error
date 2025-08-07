from apscheduler.schedulers.asyncio import AsyncIOScheduler
from api.db.task import publish_scheduled_tasks
from api.cron import send_usage_summary_stats, save_daily_traces
from api.settings import settings
from api.utils.logging import logger
from datetime import timezone, timedelta

# Create IST timezone
ist_timezone = timezone(timedelta(hours=5, minutes=30))

scheduler = AsyncIOScheduler(timezone=ist_timezone)


# Check for tasks to publish every minute
@scheduler.scheduled_job("interval", minutes=1)
async def check_scheduled_tasks():
    try:
        await publish_scheduled_tasks()
    except Exception as e:
        # Log the error but don't crash the scheduler
        logger.error(f"Error in check_scheduled_tasks: {e}")


# Send usage summary stats every day at 9 AM IST
@scheduler.scheduled_job("cron", hour=9, minute=0, timezone=ist_timezone)
async def daily_usage_stats():
    try:
        if not settings.slack_usage_stats_webhook_url:
            return

        await send_usage_summary_stats()
    except Exception as e:
        logger.error(f"Error in daily_usage_stats: {e}")


@scheduler.scheduled_job("cron", hour=10, minute=0, timezone=ist_timezone)
async def daily_traces():
    try:
        save_daily_traces()
    except Exception as e:
        logger.error(f"Error in daily_traces: {e}")
