from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config_loader import ConfigError, get_optional, load_yaml_config
from src.gold_metadata_writer import build_gold_metadata_plan, write_gold_datasets
from src.gold_transformer import build_gold_transformation_plan
from src.gold_validator import build_gold_validation_plan
from src.run_id import utc_now_iso


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the FCC Gold facts from the validated Silver dataset."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the Gold transformation YAML configuration file.",
    )
    parser.add_argument(
        "--source-run-id",
        required=True,
        help="Phase 4 Silver source run identifier to target.",
    )
    return parser.parse_args(argv)


def resolve_paths(config: dict[str, Any], source_run_id: str) -> dict[str, str]:
    silver_root = str(
        get_optional(
            config,
            "silver.output_path",
            "data/silver/fcc/consumer_complaints",
        )
    ).strip()
    silver_file_name = str(
        get_optional(
            config,
            "silver.output_file_name",
            "silver_fcc_consumer_complaints.json",
        )
    ).strip()
    daily_output_root = str(
        get_optional(
            config,
            "gold.daily_output_path",
            "data/gold/fact_complaints_daily",
        )
    ).strip()
    monthly_output_root = str(
        get_optional(
            config,
            "gold.monthly_output_path",
            "data/gold/fact_complaints_monthly",
        )
    ).strip()
    metadata_root = str(
        get_optional(
            config,
            "gold.metadata_path",
            "data/gold/_metadata",
        )
    ).strip()
    quality_root = str(
        get_optional(
            config,
            "gold.quality_path",
            "data/gold/_quality",
        )
    ).strip()

    return {
        "silver_input_file": str(
            (Path(silver_root) / source_run_id / silver_file_name).as_posix()
        ),
        "daily_output_root": str(Path(daily_output_root).as_posix()),
        "monthly_output_root": str(Path(monthly_output_root).as_posix()),
        "gold_metadata_file": str((Path(metadata_root) / f"{source_run_id}.json").as_posix()),
        "quality_output_directory": str((Path(quality_root) / source_run_id).as_posix()),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    run_start_utc = utc_now_iso()

    try:
        config = load_yaml_config(args.config)
        paths = resolve_paths(config, args.source_run_id)
        rolling_window_months = int(
            get_optional(config, "gold.rolling_window_months", 3)
        )
        if rolling_window_months <= 0:
            raise ConfigError("gold.rolling_window_months must be greater than zero.")

        transformation_plan = build_gold_transformation_plan(
            config=config,
            source_run_id=args.source_run_id,
            paths=paths,
            rolling_window_months=rolling_window_months,
        )
        output_summary = write_gold_datasets(
            daily_output_root=paths["daily_output_root"],
            monthly_output_root=paths["monthly_output_root"],
            daily_records=transformation_plan["daily_records"],
            monthly_records=transformation_plan["monthly_records"],
        )
        validation_plan = build_gold_validation_plan(
            config=config,
            source_run_id=args.source_run_id,
            paths=paths,
            daily_records=transformation_plan["daily_records"],
            monthly_records=transformation_plan["monthly_records"],
            transformation_summary=transformation_plan["summary"],
            reconciliation_inputs=transformation_plan["reconciliation_inputs"],
        )
        metadata_plan = build_gold_metadata_plan(
            config=config,
            source_run_id=args.source_run_id,
            paths=paths,
            transformation_summary=transformation_plan["summary"],
            validation_summary=validation_plan["summary"],
            output_summary=output_summary,
            run_start_utc=run_start_utc,
            run_end_utc=utc_now_iso(),
        )
    except (ConfigError, OSError, ValueError) as exc:
        print(f"Gold transformation failed: {exc}", file=sys.stderr)
        return 1

    summary = {
        "status": "gold_pipeline_complete",
        "config_path": str(Path(args.config).as_posix()),
        "source_run_id": args.source_run_id,
        "paths": paths,
        "transformation_summary": transformation_plan["summary"],
        "validation_summary": validation_plan["summary"],
        "metadata_summary": metadata_plan["summary"],
        "deferred_kpis": ["category_share"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
