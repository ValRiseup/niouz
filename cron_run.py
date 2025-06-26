#!/usr/bin/env python3
"""
Root-level cron script for Railway
This ensures the cron job runs from the correct directory
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

def main():
    """Main cron job execution"""
    start_time = datetime.now()
    logging.info(f"🕐 [ROOT-CRON] Starting cron job at {start_time}")
    
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.join(project_root, 'backend')
        cron_script = os.path.join(backend_dir, 'cron_scraper.py')
        
        logging.info(f"📁 [ROOT-CRON] Project root: {project_root}")
        logging.info(f"📁 [ROOT-CRON] Backend dir: {backend_dir}")
        logging.info(f"📁 [ROOT-CRON] Cron script: {cron_script}")
        
        # Check if files exist
        if not os.path.exists(backend_dir):
            logging.error(f"❌ [ROOT-CRON] Backend directory not found: {backend_dir}")
            return
            
        if not os.path.exists(cron_script):
            logging.error(f"❌ [ROOT-CRON] Cron script not found: {cron_script}")
            return
        
        # Environment check
        if os.environ.get('GEMINI_API_KEY'):
            logging.info("✅ [ROOT-CRON] GEMINI_API_KEY is set")
        else:
            logging.error("❌ [ROOT-CRON] GEMINI_API_KEY is missing!")
            return
        
        logging.info("🚀 [ROOT-CRON] Executing cron scraper...")
        
        # Run the cron script
        result = subprocess.run(
            ['python3', cron_script],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=1200  # 20 minutes
        )
        
        if result.returncode == 0:
            logging.info("✅ [ROOT-CRON] Cron job completed successfully")
            logging.info(f"📊 [ROOT-CRON] Output: {result.stdout[-500:]}")
        else:
            logging.error(f"❌ [ROOT-CRON] Cron job failed with code {result.returncode}")
            logging.error(f"🔥 [ROOT-CRON] Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logging.error("⏰ [ROOT-CRON] Cron job timed out")
    except Exception as e:
        logging.error(f"💥 [ROOT-CRON] Error: {e}")
    
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"🏁 [ROOT-CRON] Completed at {end_time} (duration: {duration})")

if __name__ == "__main__":
    main() 