import time
import logging
import asyncio
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, JobQueue

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Telegram Bot Token
TOKEN = "7328624662:AAEcFhLmgKJz6vgm4HqMAyXKtknXNx4h5HU"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def extract_jobs(driver):
    jobs = []
    driver.get("https://www.amazon.jobs/en/locations/canada")
    time.sleep(5)
    job_listings = driver.find_elements(By.CLASS_NAME, "job-tile")
    
    for job in job_listings:
        try:
            title = job.find_element(By.CLASS_NAME, "job-title").text
            location = job.find_element(By.CLASS_NAME, "location").text
            link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
            if "Part Time" in title:
                jobs.append({"Title": title, "Location": location, "Link": link})
        except:
            continue
    return jobs

async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! I will notify you of new Amazon part-time jobs.")

async def send_job_alerts(update: Update, context):
    driver = setup_driver()
    jobs = extract_jobs(driver)
    driver.quit()
    
    if jobs:
        for job in jobs:
            keyboard = [[InlineKeyboardButton("Apply Now", url=job["Link"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = f"📢 *New Job Alert!*\n\n*Title:* {job['Title']}\n*Location:* {job['Location']}\n[Job Link]({job['Link']})"
            await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No new part-time jobs found.")

async def stop(update: Update, context):
    await update.message.reply_text("Stopping bot...")
    exit()

# Configure AsyncIOScheduler with correct timezone
scheduler = AsyncIOScheduler(timezone=pytz.timezone("UTC"))  # Ensure pytz timezone is properly set
scheduler.start()

# Initialize Telegram Bot



# Add bot commands


async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("jobs", send_job_alerts))
    application.add_handler(CommandHandler("stop", stop))
    
    await application.initialize()
    try:
        await application.run_polling()
    finally:
        await application.shutdown()

    # Attach job queue explicitly
    job_queue = application.job_queue


if __name__ == "__main__":
    try:
        asyncio.run(main())  # Use asyncio.run() to handle the event loop properly
    except RuntimeError as e:
        print(f"RuntimeError encountered: {e}. Trying manual event loop creation.")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
