import schedule
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_URL = "http://localhost:8000/health"  # Replace with your actual API URL

def health_check():
    """Function to check API health."""
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            logging.info("✅ API is healthy: %s", response.json())
        else:
            logging.error("❌ API health check failed! Status: %d", response.status_code)
    except Exception as e:
        logging.error("❌ Error in health check: %s", str(e))

# Schedule the job to run every minute
schedule.every(1).minutes.do(health_check)

if __name__ == "__main__":
    logging.info("⏳ Scheduler started. Running health checks every minute...")
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check the schedule every second
