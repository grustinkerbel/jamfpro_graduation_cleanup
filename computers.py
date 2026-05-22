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


def normalize_computer_record(computer: Dict[str, Any]) -> Dict[str, Any]:

    general = computer.get("general", {})
    mdm_capable = general.get("mdmCapable", {})

    capable_users = mdm_capable.get("capableUsers", [])

    username = None
    if isinstance(capable_users, list) and len(capable_users) > 0:
        username = capable_users[0]

    return {

        "jamf_id": computer.get("id"),
        "computer_name": general.get("name"),
        "asset_tag": general.get("assetTag"),
        "serial_number": computer.get("hardware", {}).get("serialNumber"),
        "model": computer.get("hardware", {}).get("model"),
        "username": username,
        "last_contact_time": general.get("lastContactTime"),
        "last_reported_ip": general.get("lastReportedIpV4"),
        "managed": general.get("remoteManagement", {}).get("managed")
    }


def get_graduating_computers(
    computers: List[Dict[str, Any]],
    graduation_year: str
) -> List[Dict[str, Any]]:
    """
    Filter inventory records by graduating_computers class year.

    Example:
        username ending in 2026
    """
    graduating_computers = []

    year_suffix = str(graduation_year)[-2:]
    
    for computer in computers:

        normalized = normalize_computer_record(computer)

        username = normalized.get("username")

        if username and username.endswith(year_suffix):
            graduating_computers.append(normalized)

    logging.info(
        f"Found {len(graduating_computers)} "
        f"graduating_computers student computers"
    )

    return graduating_computers
