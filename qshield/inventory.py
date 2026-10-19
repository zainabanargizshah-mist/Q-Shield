"""
Inventory management for Q-Shield.

Handles loading demo data, importing from CSV/JSON, and managing
the asset lifecycle within the database.
"""

import os
import json
import pandas as pd
from typing import List, Tuple, Dict

from qshield.models import CryptographicAsset, ASSET_FIELDS
from qshield.database import Database
from qshield.validation import validate_file_upload, validate_dataframe


DEMO_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo_assets.csv")


def load_demo_assets() -> List[CryptographicAsset]:
    """Load the synthetic demo dataset from the bundled CSV on request."""
    path = os.path.normpath(DEMO_DATA_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Demo dataset not found: {path}")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]
    assets, errors = validate_dataframe(df)
    return assets


def import_assets_to_db(
    db: Database, assets: List[CryptographicAsset], source: str = "upload"
) -> int:
    """Import assets into the database and log the activity."""
    count = db.upsert_assets(assets)
    db.log_activity(
        action=f"Imported {count} assets",
        details=f"Source: {source}",
        asset_count=count,
    )
    return count


def get_assets_dataframe(db: Database) -> pd.DataFrame:
    """Get all assets as a pandas DataFrame."""
    assets = db.get_all_assets()
    if not assets:
        return pd.DataFrame(columns=ASSET_FIELDS)
    df = pd.DataFrame(assets)
    # Select only standard fields, ignore DB metadata
    cols = [c for c in ASSET_FIELDS if c in df.columns]
    return df[cols]


def export_assets_csv(db: Database) -> str:
    """Export assets as CSV string."""
    df = get_assets_dataframe(db)
    return df.to_csv(index=False)
