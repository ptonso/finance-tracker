import os
import gdown
import json
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

lookup_spreadsheet_id = os.getenv("LOOKUP_SPREADSHEET_ID")
sheet_name = os.getenv("LOOKUP_SHEET_PAGE")
lookup_json_path = os.getenv("CATEGORY_LOOKUP_PATH")


def download_extracts(drive_folder_id, local_folder, debug=False):
    """Download only new files from the Google Drive folder to the local folder."""

    if not len(drive_folder_id) == 33:
        print(f"folder id is not a valid google ID: {drive_folder_id}")
        pass

    print("Downloading files from drive...")

    os.makedirs(local_folder, exist_ok=True)
    folder_url = f"https://drive.google.com/drive/folders/{drive_folder_id}"
    try:
        gdown.download_folder(folder_url, output=local_folder, quiet=not debug)
    except Exception as e:
        print(f"gdown could not download the extract csv files. Error: {e}")

    print("All extracted downloaded!")

