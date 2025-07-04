import os
import shutil
from copy import deepcopy
from typing import Any, Dict

from src.pipeline.download import donwload_data
from src.pipeline.clean import clean_data
from src.pipeline.categorize import categorize_data
from src.pipeline.reconcile import reconcile_data
from src.utils.config import load_config
from src.logger import setup_logger

logger = setup_logger(__name__)


def build_tmp_config(orig_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a copy of orig_config where every data_* path is rewritten:
      "data/.../" → "data/tmp/.../"
    so that the pipeline writes into data/tmp/ instead of data/.
    """
    tmp_config = deepcopy(orig_config)
    for key, path in orig_config["paths"].items():
        if key.startswith("data_"):
            # Compute the subpath after "data/"
            rel = os.path.relpath(path, "data")
            # New path: data/tmp/<rel>
            tmp_path = os.path.join("data", "tmp", rel)
            tmp_config["paths"][key] = os.path.normpath(tmp_path) + os.sep
    return tmp_config

def replace_tmp_with_data(config: Dict[str, Any]) -> None:
    """
    For each pipeline output folder under data/tmp (00--raw, 01--cleaned,
    02--categorized, 03--reconciled), delete the corresponding folder under data/
    if it exists, then move data/tmp/<folder> → data/<folder>. Leave any other
    subfolders in data/ (e.g. lookup, dashboards) untouched. If data/tmp becomes
    empty, remove it.
    """
    pipeline_keys = ["data_raw", "data_cleaned", "data_categorized", "data_reconciled"]
    moved_any = False

    for key in pipeline_keys:
        tmp_path = config["paths"].get(key, "")
        if not tmp_path.startswith("data/tmp/"):
            logger.error(f"Expected tmp path under data/tmp/: {tmp_path}")
            return

        target_path = tmp_path.replace(os.path.normpath("data/tmp/"), os.path.normpath("data/"))
        tmp_path_norm = os.path.normpath(tmp_path)
        target_path_norm = os.path.normpath(target_path)

        # Verify tmp folder exists and is not empty
        if not os.path.isdir(tmp_path_norm) or not os.listdir(tmp_path_norm):
            logger.error(f"Cannot replace data: missing or empty tmp folder: {tmp_path_norm}")
            return

        # If target exists already, delete it
        if os.path.exists(target_path_norm):
            try:
                shutil.rmtree(target_path_norm)
                logger.info(f"Removed existing folder at {target_path_norm}")
            except Exception as e:
                logger.error(f"Failed to remove {target_path_norm}: {e}")
                return

        # Ensure parent of target exists (e.g. data/)
        parent_dir = os.path.dirname(target_path_norm)
        os.makedirs(parent_dir, exist_ok=True)

        # Move tmp → target
        try:
            shutil.move(tmp_path_norm, target_path_norm)
            logger.info(f"Moved {tmp_path_norm} → {target_path_norm}")
            moved_any = True
        except Exception as e:
            logger.error(f"Failed to move {tmp_path_norm} to {target_path_norm}: {e}")
            return

    # If we moved at least one folder, attempt to remove data/tmp/ if empty
    tmp_root = os.path.normpath(os.path.join(config["paths"]["data_raw"], os.pardir))
    if moved_any and os.path.isdir(tmp_root) and not os.listdir(tmp_root):
        try:
            os.rmdir(tmp_root)
            logger.info(f"Removed empty tmp folder {tmp_root}")
        except Exception as e:
            logger.error(f"Failed to remove {tmp_root}: {e}")


def main() -> None:
    orig_config = load_config()
    config      = build_tmp_config(orig_config)

    logger.info("Downloading data from sheets...")
    donwload_data(config)
    logger.info("Cleaning data from raw...")
    clean_data(config)
    logger.info("Categorizing data from cleaned...")
    categorize_data(config)
    logger.info("Reconciling data from categorized...")
    reconcile_data(config)
    replace_tmp_with_data(config)
    logger.info("All done!")


if __name__ == "__main__":
    main()
