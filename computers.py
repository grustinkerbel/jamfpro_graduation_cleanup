"""
Jamf Pro Computer Inventory Functions
-------------------------------------
Utilities for retrieving, filtering, and processing
Jamf Pro computer inventory data.
"""

import logging
import requests

from typing import List, Dict, Any


DEFAULT_SECTIONS = [
    "GENERAL",
    "HARDWARE",
    "USER_AND_LOCATION"
]


def get_nested(
    record: Dict[str, Any],
    keys: List[str],
    default=None
):
    """
    Safely retrieve nested dictionary values.
    """

    value = record

    for key in keys:

        if not isinstance(value, dict):
            return default

        value = value.get(key)

        if value is None:
            return default

    return value


def get_all_computers(
    base_url: str,
    token: str,
    sections: List[str] = None,
    page_size: int = 100,
    sort: str = "general.assetTag"
) -> List[Dict[str, Any]]:
    """
    Retrieve all computer inventory records from Jamf Pro.
    """

    if sections is None:
        sections = DEFAULT_SECTIONS

    computers = []

    page = 0

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    params = {
        "section": sections,
        "page-size": page_size,
        "sort": sort
    }

    base_url = base_url.rstrip("/")

    url = f"{base_url}/api/v1/computers-inventory"

    while True:

        params["page"] = page

        try:

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            results = data.get("results", [])

            if not results:
                break

            computers.extend(results)

            logging.info(
                f"Retrieved page {page} "
                f"({len(results)} records)"
            )

            page += 1

        except requests.exceptions.RequestException as err:

            logging.error(
                f"Failed retrieving page {page}: {err}"
            )

            break

    logging.info(
        f"Retrieved {len(computers)} total computers"
    )

    return computers


def normalize_computer_record(
    computer: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Normalize Jamf computer inventory record into
    a simplified structure for automation workflows.
    """

    return {

        "jamf_id":
            get_nested(computer, ["id"]),

        "computer_name":
            get_nested(computer, ["general", "name"]),

        "asset_tag":
            get_nested(computer, ["general", "assetTag"]),

        "serial_number":
            get_nested(computer, ["hardware", "serialNumber"]),

        "model":
            get_nested(computer, ["hardware", "model"]),

        "processor_type":
            get_nested(computer, ["hardware", "processorType"]),

        "username":
            get_nested(computer, ["userAndLocation", "username"]),

        "real_name":
            get_nested(computer, ["userAndLocation", "realname"]),

        "email":
            get_nested(computer, ["userAndLocation", "email"]),

        "last_contact_time":
            get_nested(computer, ["general", "lastContactTime"]),

        "last_reported_ip":
            get_nested(computer, ["general", "lastReportedIp"]),

        "managed":
            get_nested(computer, ["general", "remoteManagement", "managed"])
    }


def get_graduating_computers(
    computers: List[Dict[str, Any]],
    graduation_year: str
) -> List[Dict[str, Any]]:
    """
    Filter inventory records by graduating class year.

    Example:
        username ending in 2026
    """

    graduating_computers = []

    for computer in computers:

        normalized = normalize_computer_record(computer)

        username = normalized.get("username")

        if not username:
            continue

        if username.endswith(graduation_year):

            graduating_computers.append(normalized)

    logging.info(
        f"Found {len(graduating_computers)} "
        f"graduating student computers"
    )

    return graduating_computers