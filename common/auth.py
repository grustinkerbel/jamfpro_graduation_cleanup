"""
Jamf Pro Authentication
------------------------------
Python utility for authenticating with the Jamf Pro API using OAuth2 Client Credentials.

Author: William Galway
Version: 1.1
"""

import logging
import requests
from typing import Optional, Dict


def get_jamf_token(
    base_url: str,
    client_id: str,
    client_secret: str,
    timeout: int = 30
) -> Optional[Dict]:
    """
    Authenticate with Jamf Pro API using OAuth2 Client Credentials.

    Args:
        base_url (str):
            Jamf Pro URL (example: https://company.jamfcloud.com)

        client_id (str):
            OAuth Client ID

        client_secret (str):
            OAuth Client Secret

        timeout (int):
            HTTP request timeout in seconds

    Returns:
        Optional[Dict]:
            Dictionary containing:
                {
                    "access_token": str,
                    "expires_in": int,
                    "token_type": str
                }

            Returns None on failure.
    """

    base_url = base_url.rstrip("/")

    token_url = f"{base_url}/api/oauth/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    try:
        logging.info("Requesting Jamf Pro access token")

        response = requests.post(
            token_url,
            data=payload,
            headers=headers,
            timeout=timeout
        )

        response.raise_for_status()

        token_data = response.json()

        logging.info("Jamf Pro authentication successful")

        return {
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in"),
            "token_type": token_data.get("token_type")
        }

    except requests.exceptions.Timeout:
        logging.error("Jamf Pro authentication request timed out")

    except requests.exceptions.HTTPError as err:
        logging.error(
            f"Jamf Pro authentication failed "
            f"(HTTP {response.status_code}): {err}"
        )

    except requests.exceptions.RequestException as err:
        logging.error(f"Jamf Pro authentication failed: {err}")

    return None