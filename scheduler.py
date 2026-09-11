from apscheduler.schedulers.blocking import BlockingScheduler

from app.jobs.kpmg_sync_job import synchronize_kpmg_reports


scheduler = BlockingScheduler(
    timezone="Europe/Istanbul"
)

scheduler.add_job(
    synchronize_kpmg_reports,
    trigger="cron",
    day_of_week="mon",
    hour=9,
    minute=0,
    id="kpmg-weekly-sync",
    replace_existing=True,
    max_instances=1,
)

if __name__ == "__main__":
    synchronize_kpmg_reports()

    print("Scheduler çalışıyor.")
    print("Sonraki otomatik kontrol: Pazartesi 09.00")

    scheduler.start()
