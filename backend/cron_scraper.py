#!/usr/bin/env python3
"""
Cron job script for running the AI news scraper
This script runs independently of the Flask server
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def run_scraper():
    """Run the news scraper"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_path = os.path.join(script_dir, 'scraper.py')
        
        logging.info("🚀 [CRON] Starting scheduled scraper run...")
        logging.info(f"🚀 [CRON] Script path: {scraper_path}")
        
        # Run the scraper in normal mode (new articles only)
        result = subprocess.run(
            ['python', scraper_path],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            logging.info("✅ [CRON] Scraper completed successfully")
            logging.info(f"📊 [CRON] Output: {result.stdout[-500:]}")  # Last 500 chars
        else:
            logging.error(f"❌ [CRON] Scraper failed with return code {result.returncode}")
            logging.error(f"🔥 [CRON] Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logging.error("⏰ [CRON] Scraper timed out after 30 minutes")
    except Exception as e:
        logging.error(f"💥 [CRON] Unexpected error: {e}")

if __name__ == "__main__":
    start_time = datetime.now()
    logging.info(f"🕐 [CRON] Cron job started at {start_time}")
    
    run_scraper()
    
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"🏁 [CRON] Cron job completed at {end_time}")
    logging.info(f"⏱️  [CRON] Total duration: {duration}") 