"""Run local batch scoring from the command line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.batch import score_csv
from app.config import settings
from app.model import ModelArtifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch score a CSV file.")
    parser.add_argument("--input", default="data/batch_scoring_input.csv")
    parser.add_argument("--output", default="data/batch_scoring_output.csv")
    args = parser.parse_args()
    model = ModelArtifact.from_path(settings.model_registry_path)
    rows = score_csv(Path(args.input), Path(args.output), model)
    print(f"Scored {rows} rows -> {args.output}")


if __name__ == "__main__":
    main()
