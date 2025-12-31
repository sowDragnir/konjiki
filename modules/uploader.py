import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ========= CONFIG =========
SESSION_PATH = os.path.abspath("konjiki_session")
WINDOW_SIZE = "1920,1080"


# ========= DRIVER =========
def get_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={SESSION_PATH}")
    options.add_argument("--profile-directory=Default")
    #options.add_argument("--headless=new")   # quitar SOLO para login inicial
    options.add_argument(f"--window-size={WINDOW_SIZE}")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36"
    )

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# ========= YOUTUBE SHORTS =========
def upload_youtube_short(driver, video_path, title):
    driver.get("https://studio.youtube.com/")
    wait = WebDriverWait(driver, 40)

    upload_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "upload-icon"))
    )
    upload_btn.click()

    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
    file_input.send_keys(os.path.abspath(video_path))

    title_box = wait.until(
        EC.presence_of_element_located((By.ID, "textbox"))
    )
    title_box.clear()
    title_box.send_keys(f"{title} #shorts")

    for _ in range(3):
        next_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "next-button"))
        )
        next_btn.click()
        time.sleep(2)

    done_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "done-button"))
    )
    done_btn.click()

    print("✅ Subido a YouTube Shorts")


# ========= INSTAGRAM REELS =========
def upload_instagram_reel(driver, video_path, caption):
    driver.get("https://www.instagram.com/")
    wait = WebDriverWait(driver, 40)

    create_btn = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//svg[@aria-label='Nueva publicación']")
        )
    )
    create_btn.click()

    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
    file_input.send_keys(os.path.abspath(video_path))

    time.sleep(8)

    for _ in range(2):
        next_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Siguiente']"))
        )
        next_btn.click()
        time.sleep(4)

    caption_box = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@aria-label='Escribe una descripción…']")
        )
    )
    caption_box.send_keys(caption)

    share_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[text()='Compartir']"))
    )
    share_btn.click()

    print("✅ Subido a Instagram Reels")


# ========= TIKTOK (ADVERTENCIA) =========
def upload_tiktok(driver, video_path, caption):
    """
    TikTok es MUY agresivo contra bots.
    Esto puede funcionar, pero NO es 100% seguro.
    Recomendado usar API oficial o servicio externo.
    """

    driver.get("https://www.tiktok.com/upload")
    wait = WebDriverWait(driver, 40)

    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(os.path.abspath(video_path))

    time.sleep(10)

    caption_box = wait.until(
        EC.presence_of_element_located((By.XPATH, "//textarea"))
    )
    caption_box.send_keys(caption)

    post_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Publicar')]"))
    )
    post_btn.click()

    print("⚠️ Subido a TikTok (riesgo)")


# ========= MASTER =========
def upload_all(video_path, title="Konjiki Clip"):
    driver = get_driver()
    try:
        upload_youtube_short(driver, video_path, title)
        upload_instagram_reel(driver, video_path, f"{title} #reels #shorts")
        # upload_tiktok(driver, video_path, title)  # activar bajo tu riesgo
    finally:
        driver.quit()
