from pathlib import Path, PurePosixPath
from typing import Optional
from pathlib import Path

import pandas as pd


class ParquetReader:
	def __init__(self, data_root: Optional[str] = None):
		self.data_root = Path(data_root) if data_root else None

	def process(self, path: str, include_subfolders: bool = False) -> pd.DataFrame:
		posix_path = PurePosixPath(path.replace("\\", "/"))
		if self.data_root and posix_path.is_absolute() and posix_path.parts[1] == "parquet_data":
			dataset_path = self.data_root.joinpath(*posix_path.parts[2:])
		else:
			dataset_path = Path(path)
		if not dataset_path.is_dir():
			raise FileNotFoundError(f"Parquet dataset directory not found: {dataset_path}")

		parquet_files = sorted(
			dataset_path.rglob("*.parquet")
			if include_subfolders
			else dataset_path.glob("*.parquet")
		)
		if not parquet_files:
			return pd.DataFrame()

		frames = [pd.read_parquet(parquet_file) for parquet_file in parquet_files]
		return pd.concat(frames, ignore_index=True, sort=False)
