"""
Jamf Graduation Device Cleanup

Author: William Galway
Date: 2026-05-22
Version: 1.0

Description:
Retrieves Jamf Pro computer inventory records and identifies
graduating student devices based on username suffix matching
the current graduation year.
"""

import os
import sys
import logging

from datetime import datetime

from common.auth import get_jamf_token
from jamf.computers import (
    get_all_computers,
    get_graduating_computers
)

from utils.logging_setup import setup_logging


# =========================================================
#                      CONFIGURATION
# =========================================================

CLIENT_ID = os.getenv("JAMF_CLIENT_ID")
CLIENT_SECRET = os.getenv("JAMF_CLIENT_SECRET")

jamf_pro_url = "https://nmh.jamfcloud.com"

CURRENT_YEAR = str(datetime.now().year)

if not all([CLIENT_ID, CLIENT_SECRET]):
    raise ValueError("Missing one or more credentials.")

logfile = "/home/wgalway/logs/jamf_graduation_cleanup.log"

logger = setup_logging(logfile)

logger.info("Script started")
logger.info(f"Python version: {sys.version}")
logger.info("Jamf Graduation Cleanup initialized")

json_filename = "graduating_devices.json"
csv_filename = "graduating_devices.csv"


# =========================================================
#                          MAIN
# =========================================================

def main():

    try:

        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------

        auth = get_jamf_token(
            jamf_pro_url,
            CLIENT_ID,
            CLIENT_SECRET
        )

        if not auth:

            logger.error("Authentication failed")

            return

        token = auth["access_token"]

        logger.info("Authentication successful")

        # -------------------------------------------------
        # RETRIEVE COMPUTER INVENTORY
        # -------------------------------------------------

        computers = get_all_computers(
            base_url=jamf_pro_url,
            token=token
        )

        logger.info(
            f"Retrieved {len(computers)} "
            f"computer inventory records"
        )

        # -------------------------------------------------
        # FILTER GRADUATING DEVICES
        # -------------------------------------------------

        graduating_computers = get_graduating_computers(
            computers=computers,
            graduation_year=CURRENT_YEAR
        )

        # -------------------------------------------------
        # DISPLAY RESULTS
        # -------------------------------------------------

        for computer in graduating_computers:

            logger.info(
                f"{computer['username']} | "
                f"{computer['computer_name']} | "
                f"{computer['serial_number']}"
            )

        logger.info("Process completed successfully")

    except Exception as e:

        logger.error(
            f"Error during graduation cleanup workflow: {e}"
        )

    finally:

        logger.info("Script finished")


if __name__ == "__main__":
    main()