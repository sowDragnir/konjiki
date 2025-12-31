import os, time, schedule
from config import *
from jobs.queue import init_db, add_job, mark_done, mark_failed
from modules.downloader import download
from modules.editor import make_short
from modules.subtitles import add_subtitles
from modules.uploader import upload_all
from modules.logger import logger

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

def job():
    conn = init_db()
    vid = str(int(time.time()))
    add_job(conn, vid)
    try:
        raw = download(CHANNELS[0], vid, RAW_DIR)
        short = f"{OUT_DIR}/{vid}_short.mp4"
        final = f"{OUT_DIR}/{vid}_final.mp4"
        make_short(raw, short)
        #add_subtitles(short, final)
        upload_all(final)
        mark_done(conn, vid)
        logger.info("JOB OK")
        os.remove(raw); os.remove(short); os.remove(final)
    except Exception:
        logger.exception("JOB ERROR")
        mark_failed(conn, vid)
    finally:
        conn.close()

job()
    

logger.info("KONJIKI v3 ONLINE")
while True:
    logger.info("Checking scheduled jobs...")
    schedule.run_pending()
    time.sleep(5)
