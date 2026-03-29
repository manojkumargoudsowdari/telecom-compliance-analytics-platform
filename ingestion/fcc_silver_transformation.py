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
from src.run_id import utc_now_iso
from src.silver_metadata_writer import build_silver_metadata_plan, write_silver_dataset
from src.silver_rejects import build_silver_reject_plan
from src.silver_transformer import build_silver_transformation_plan
from src.silver_validator import build_silver_validation_plan


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold entry point for the FCC Silver transformation pipeline."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the Silver transformation YAML configuration file.",
    )
    parser.add_argument(
        "--source-run-id",
        required=True,
        help="Phase 3 raw ingestion run identifier to target.",
    )
    return parser.parse_args(argv)


def resolve_paths(config: dict[str, Any], source_run_id: str) -> dict[str, str]:
    raw_root = str(
        get_optional(
            config,
            "input.raw_path",
            get_optional(config, "output.raw_path", "data/raw/fcc/consumer_complaints"),
        )
    ).strip()
    raw_metadata_root = str(
        get_optional(
            config,
            "input.metadata_path",
            get_optional(config, "output.metadata_path", "data/raw/fcc/_metadata"),
        )
    ).strip()
    silver_root = str(
        get_optional(
            config,
            "silver.output_path",
            "data/silver/fcc/consumer_complaints",
        )
    ).strip()
    silver_metadata_root = str(
        get_optional(
            config,
            "silver.metadata_path",
            "data/silver/fcc/_metadata",
        )
    ).strip()
    reject_root = str(
        get_optional(
            config,
            "silver.reject_path",
            "data/silver/fcc/_rejects",
        )
    ).strip()
    quality_root = str(
        get_optional(
            config,
            "silver.quality_path",
            "data/silver/fcc/_quality",
        )
    ).strip()

    return {
        "raw_input_directory": str((Path(raw_root) / source_run_id).as_posix()),
        "raw_metadata_file": str((Path(raw_metadata_root) / f"{source_run_id}.json").as_posix()),
        "silver_output_directory": str((Path(silver_root) / source_run_id).as_posix()),
        "silver_metadata_file": str(
            (Path(silver_metadata_root) / f"{source_run_id}.json").as_posix()
        ),
        "reject_output_directory": str((Path(reject_root) / source_run_id).as_posix()),
        "quality_output_directory": str((Path(quality_root) / source_run_id).as_posix()),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    run_start_utc = utc_now_iso()

    try:
        config = load_yaml_config(args.config)
        paths = resolve_paths(config, args.source_run_id)
        transformation_plan = build_silver_transformation_plan(
            config=config,
            source_run_id=args.source_run_id,
            paths=paths,
            include_records=True,
        )
        validation_plan = build_silver_validation_plan(
            config=config,
            source_run_id=args.source_run_id,
            paths=paths,
            final_candidate_records=transformation_plan[
                "final_deduplicated_candidate_records"
            ],
        )
        reject_plan = build_silver_reject_plan(
            config=config,
            source_run_id=args.source_run_id,
            paths=paths,
            candidate_reject_records=transformation_plan["candidate_reject_records"],
            reject_timestamp_utc=transformation_plan["summary"][
                "silver_processed_at_utc"
            ],
        )
        silver_output_path = None
        if validation_plan["summary"]["validation_passed"]:
            output_path = write_silver_dataset(
                paths["silver_output_directory"],
                transformation_plan["final_deduplicated_candidate_records"],
            )
            silver_output_path = output_path.as_posix()
        metadata_plan = build_silver_metadata_plan(
            config=config,
            source_run_id=args.source_run_id,
            paths=paths,
            transformation_summary=transformation_plan["summary"],
            validation_summary=validation_plan["summary"],
            reject_summary=reject_plan["summary"],
            silver_output_path=silver_output_path,
            run_start_utc=run_start_utc,
            run_end_utc=utc_now_iso(),
        )
    except (ConfigError, OSError, ValueError) as exc:
        print(f"Silver transformation scaffold failed: {exc}", file=sys.stderr)
        return 1

    summary = {
        "status": "silver_pipeline_complete",
        "config_path": str(Path(args.config).as_posix()),
        "source_run_id": args.source_run_id,
        "paths": paths,
        "transformation_summary": transformation_plan["summary"],
        "validation_summary": validation_plan["summary"],
        "reject_summary": reject_plan["summary"],
        "metadata_summary": metadata_plan["summary"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
