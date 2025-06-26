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
import signal

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def timeout_handler(signum, frame):
    raise TimeoutError("Cron job timed out")

def run_scraper():
    """Run the news scraper with timeout protection"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_path = os.path.join(script_dir, 'scraper.py')
        
        logging.info("🚀 [CRON] Starting scheduled scraper run...")
        logging.info(f"🚀 [CRON] Script path: {scraper_path}")
        logging.info(f"🚀 [CRON] Working directory: {script_dir}")
        
        # Check environment
        if os.environ.get('GEMINI_API_KEY'):
            logging.info("✅ [CRON] GEMINI_API_KEY is set")
        else:
            logging.error("❌ [CRON] GEMINI_API_KEY is missing!")
            return
        
        # Set timeout alarm
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1200)  # 20 minutes timeout
        
        # Run the scraper in normal mode (new articles only)
        result = subprocess.run(
            ['python', scraper_path],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=1200  # 20 minutes timeout
        )
        
        # Cancel timeout
        signal.alarm(0)
        
        if result.returncode == 0:
            logging.info("✅ [CRON] Scraper completed successfully")
            # Log last 1000 chars instead of 500 for better debugging
            output_preview = result.stdout[-1000:] if result.stdout else "No output"
            logging.info(f"📊 [CRON] Output preview: ...{output_preview}")
        else:
            logging.error(f"❌ [CRON] Scraper failed with return code {result.returncode}")
            logging.error(f"🔥 [CRON] Error output: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logging.error("⏰ [CRON] Scraper timed out after 20 minutes")
        # Kill any hanging processes
        try:
            result.kill()
        except:
            pass
    except TimeoutError:
        logging.error("⏰ [CRON] Cron job exceeded maximum time limit")
    except Exception as e:
        logging.error(f"💥 [CRON] Unexpected error: {e}")
        logging.error(f"💥 [CRON] Error type: {type(e).__name__}")
    finally:
        # Ensure alarm is cancelled
        try:
            signal.alarm(0)
        except:
            pass

if __name__ == "__main__":
    start_time = datetime.now()
    logging.info(f"🕐 [CRON] Cron job started at {start_time}")
    logging.info(f"🌍 [CRON] Environment: {'Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development'}")
    
    try:
        run_scraper()
    except KeyboardInterrupt:
        logging.info("🛑 [CRON] Cron job interrupted by user")
    except Exception as e:
        logging.error(f"💥 [CRON] Fatal error: {e}")
    
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"🏁 [CRON] Cron job completed at {end_time}")
    logging.info(f"⏱️  [CRON] Total duration: {duration}")
    
    # Ensure clean exit
    sys.exit(0) 