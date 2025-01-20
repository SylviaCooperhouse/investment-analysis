from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import os

# Define the task to fetch data and calculate VaR
def fetch_and_calculate_var():
    print(f"Running task at {datetime.now()}...")
    # Fetch data from crypto and stocks
    os.system('python data_fetch/fetch_crypto.py')
    os.system('python data_fetch/fepython scheduler.pytch_stocks.py')
    # Calculate VaR
    os.system('python VaR.py')

# Initialize the scheduler
scheduler = BlockingScheduler()
# Schedule the task to run daily at 6:00 AM
scheduler.add_job(fetch_and_calculate_var, 'cron', hour=6)

print("Scheduler started. Press Ctrl+C to exit.")
# Start the scheduler
scheduler.start()



# Add a CLI option to your script for a manual run
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", action="store_true", help="Run the task manually")
    args = parser.parse_args()

    if args.manual:
        fetch_and_calculate_var()
    else:
        scheduler.start()

