"""Audit the KAMP welding dataset and build a daily quality summary."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd


HERE = Path(__file__).resolve().parent
RSW_ROOT = HERE.parent
PROJECT_ROOT = RSW_ROOT.parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "kamp_welding"
WORKBOOK_PATH = DATA_DIR / "Welding Data Set_01.xlsx"
SCALED_PATH = DATA_DIR / "scaled_data.csv"
OUTPUT_DIR = HERE / "outputs"
PROFILE_CSV = OUTPUT_DIR / "kamp_dataset_profile.csv"
PROFILE_MD = OUTPUT_DIR / "kamp_dataset_profile.md"
DAILY_CSV = OUTPUT_DIR / "kamp_daily_quality_summary.csv"

PROCESS_COLUMNS = {
    "force": "weld force(bar)",
    "current": "weld current(kA)",
    "voltage": "weld Voltage(v)",
    "weld_time": "weld time(ms)",
}


def read_scaled_csv(path: Path = SCALED_PATH) -> tuple[pd.DataFrame, str]:
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to detect CSV encoding: {path}")


def detect_sheets(path: Path = WORKBOOK_PATH) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    sheets = pd.read_excel(path, sheet_name=None)
    roles: dict[str, str] = {}
    for name, frame in sheets.items():
        columns = {str(column).strip().lower() for column in frame.columns}
        if set(PROCESS_COLUMNS.values()).issubset(frame.columns):
            roles["raw"] = name
        elif {"defect", "defect type"}.issubset(columns):
            roles["result"] = name
        elif {"data", "항목 설명"}.issubset(columns):
            roles["dictionary"] = name
    if "raw" not in roles or "result" not in roles:
        raise ValueError(f"Required raw/result sheets were not detected. Detected roles: {roles}")
    return sheets, roles


def determine_label_granularity(raw: pd.DataFrame, result: pd.DataFrame) -> tuple[str, str]:
    raw_label_columns = [
        column
        for column in raw.columns
        if "defect" in str(column).lower() or "불량" in str(column)
    ]
    if raw_label_columns:
        return "per_weld", f"Raw data contains label-like columns: {raw_label_columns}"
    if "defect" not in result or "defect type" not in result:
        return "unavailable", "Result sheet has no interpretable defect count/type columns."
    if len(result) >= len(raw):
        return "unavailable", "Result structure is not clearly aggregate or per-weld."
    return (
        "daily_aggregate",
        "Result rows are date/defect-type counts; no key maps each raw weld to one defect label.",
    )


def build_daily_summary(raw: pd.DataFrame, result: pd.DataFrame) -> pd.DataFrame:
    raw = raw.copy()
    result = result.copy()
    raw["date"] = pd.to_datetime(raw["working time"], errors="coerce").dt.date
    result["date"] = pd.to_datetime(result["working time"], errors="coerce").dt.date

    aggregations: dict[str, tuple[str, str]] = {"n_welds": ("idx", "count")}
    for prefix, column in PROCESS_COLUMNS.items():
        for statistic in ("mean", "std", "min", "max"):
            aggregations[f"{prefix}_{statistic}"] = (column, statistic)
    daily = raw.groupby("date", dropna=False).agg(**aggregations).reset_index()

    defects = result.groupby("date", dropna=False)["defect"].sum().rename("defect_count_total")
    type_counts = result.pivot_table(
        index="date", columns="defect type", values="defect", aggfunc="sum", fill_value=0
    )
    type_counts = type_counts.rename(
        columns={column: f"defect_type_{int(column)}_count" for column in type_counts.columns}
    )
    daily = daily.merge(defects, on="date", how="left").merge(type_counts, on="date", how="left")
    for column in ("defect_type_1_count", "defect_type_2_count", "defect_type_3_count"):
        if column not in daily:
            daily[column] = pd.NA
    daily["defect_rate"] = daily["defect_count_total"] / daily["n_welds"]
    return daily


def _profile_row(source: str, sheet: str, metric: str, value: Any, notes: str = "") -> dict[str, Any]:
    return {"source": source, "sheet": sheet, "metric": metric, "value": value, "notes": notes}


def build_profile_rows(
    sheets: dict[str, pd.DataFrame],
    roles: dict[str, str],
    scaled: pd.DataFrame,
    scaled_encoding: str,
    label_granularity: str,
    label_reason: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, frame in sheets.items():
        rows.extend(
            [
                _profile_row("xlsx", name, "rows", len(frame)),
                _profile_row("xlsx", name, "columns", len(frame.columns)),
                _profile_row("xlsx", name, "column_names", " | ".join(map(str, frame.columns))),
                _profile_row("xlsx", name, "missing_values", int(frame.isna().sum().sum())),
                _profile_row("xlsx", name, "duplicate_rows", int(frame.duplicated().sum())),
            ]
        )
        rows.extend(
            _profile_row("xlsx", name, f"missing::{column}", int(frame[column].isna().sum()))
            for column in frame.columns
        )
    raw = sheets[roles["raw"]]
    result = sheets[roles["result"]]
    raw_dates = pd.to_datetime(raw["working time"], errors="coerce")
    rows.extend(
        [
            _profile_row("xlsx", roles["raw"], "date_min", raw_dates.min().date()),
            _profile_row("xlsx", roles["raw"], "date_max", raw_dates.max().date()),
            _profile_row("xlsx", roles["raw"], "date_unique_count", raw_dates.nunique()),
            _profile_row("xlsx", roles["raw"], "machine_unique_count", raw["Machine_Name"].nunique()),
            _profile_row("xlsx", roles["raw"], "item_unique_count", raw["Item No"].nunique()),
            _profile_row("xlsx", roles["result"], "defect_count_total", int(result["defect"].sum())),
            _profile_row(
                "xlsx",
                roles["result"],
                "defect_type_unique_count",
                result["defect type"].nunique(),
            ),
            _profile_row("assessment", "label", "label_granularity", label_granularity, label_reason),
        ]
    )
    for prefix, column in PROCESS_COLUMNS.items():
        for statistic, value in raw[column].describe().items():
            rows.append(_profile_row("xlsx", roles["raw"], f"{prefix}_{statistic}", value))
    rows.extend(
        [
            _profile_row("csv", SCALED_PATH.name, "encoding", scaled_encoding),
            _profile_row("csv", SCALED_PATH.name, "rows", len(scaled)),
            _profile_row("csv", SCALED_PATH.name, "columns", len(scaled.columns)),
            _profile_row("csv", SCALED_PATH.name, "column_names", " | ".join(map(str, scaled.columns))),
            _profile_row("csv", SCALED_PATH.name, "missing_values", int(scaled.isna().sum().sum())),
            _profile_row("csv", SCALED_PATH.name, "duplicate_rows", int(scaled.duplicated().sum())),
            _profile_row(
                "assessment",
                "scaled_data",
                "row_count_matches_raw",
                len(scaled) == len(raw),
            ),
            _profile_row(
                "assessment",
                "scaled_data",
                "label_column_present",
                any("defect" in str(column).lower() or "불량" in str(column) for column in scaled),
            ),
        ]
    )
    rows.extend(
        _profile_row(
            "csv",
            SCALED_PATH.name,
            f"missing::{column}",
            int(scaled[column].isna().sum()),
        )
        for column in scaled.columns
    )
    return rows


def write_profile_markdown(
    sheets: dict[str, pd.DataFrame],
    roles: dict[str, str],
    scaled: pd.DataFrame,
    scaled_encoding: str,
    label_granularity: str,
    label_reason: str,
    daily: pd.DataFrame,
) -> None:
    raw = sheets[roles["raw"]]
    result = sheets[roles["result"]]
    dates = pd.to_datetime(raw["working time"], errors="coerce")
    sheet_lines = [
        "| sheet | rows | columns | missing | duplicates |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, frame in sheets.items():
        sheet_lines.append(
            f"| {name} | {len(frame)} | {len(frame.columns)} | "
            f"{int(frame.isna().sum().sum())} | {int(frame.duplicated().sum())} |"
        )
    process_lines = [
        "| variable | mean | std | min | max |",
        "|---|---:|---:|---:|---:|",
    ]
    for prefix, column in PROCESS_COLUMNS.items():
        process_lines.append(
            f"| {prefix} | {raw[column].mean():.6f} | {raw[column].std():.6f} | "
            f"{raw[column].min():.6f} | {raw[column].max():.6f} |"
        )
    lines = [
        "# KAMP Welding Dataset Profile",
        "",
        "## Dataset structure",
        "",
        *sheet_lines,
        "",
        f"- Scaled CSV: {len(scaled)} rows x {len(scaled.columns)} columns, encoding `{scaled_encoding}`.",
        f"- Scaled CSV row count matches raw data: `{len(scaled) == len(sheets[roles['raw']])}`.",
        f"- Scaled CSV missing values: {int(scaled.isna().sum().sum())}; label column present: "
        f"`{any('defect' in str(column).lower() or '불량' in str(column) for column in scaled)}`.",
        "- The dataset contains per-weld process-variable logs for force, current, voltage, and weld time.",
        "",
        "## Raw process-log coverage",
        "",
        f"- Date range: {dates.min().date()} to {dates.max().date()} ({dates.nunique()} unique dates).",
        f"- Machine_Name unique count: {raw['Machine_Name'].nunique()}.",
        f"- Item No unique count: {raw['Item No'].nunique()}.",
        "",
        *process_lines,
        "",
        "## Result sheet structure",
        "",
        f"- Rows: {len(result)}; total reported defect count: {int(result['defect'].sum())}; "
        f"defect types: {result['defect type'].nunique()}.",
        "- Result `idx` values are result-row sequence values. Although they overlap the first raw "
        "row indices, each result row contains a defect count and defect type, so this is not a "
        "one-to-one per-weld label.",
        "",
        "## Label granularity decision",
        "",
        f"- Declared granularity: **{label_granularity}**",
        f"- Reason: {label_reason}",
        "- The result sheet is interpreted as date/type aggregate defect counts, not per-weld labels.",
        "- Per-weld supervised defect prediction is therefore not supported.",
        f"- Daily rows with matched defect counts: {int(daily['defect_count_total'].notna().sum())} "
        f"of {len(daily)}.",
        "",
        "## Supported use",
        "",
        "- Descriptive daily defect-rate estimation.",
        "- Suggested-only calibration of the RSW synthetic defect-risk proxy.",
        "",
        "## Not supported",
        "",
        "- PM scheduling validation",
        "- Tip dressing timing validation",
        "- Maintenance slot validation",
        "- Downtime validation",
        "- Electrode wear or HI calibration",
        "- The dataset does not include PM history, tip dressing history, maintenance slots, or downtime.",
        "",
        "This is not real factory validation. The KAMP data can only support a partial external-data "
        "quality-risk recheck.",
    ]
    PROFILE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sheets, roles = detect_sheets()
    raw = sheets[roles["raw"]]
    result = sheets[roles["result"]]
    scaled, scaled_encoding = read_scaled_csv()
    label_granularity, label_reason = determine_label_granularity(raw, result)
    daily = build_daily_summary(raw, result)
    daily.to_csv(DAILY_CSV, index=False, encoding="utf-8")
    rows = build_profile_rows(
        sheets, roles, scaled, scaled_encoding, label_granularity, label_reason
    )
    with PROFILE_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source", "sheet", "metric", "value", "notes"])
        writer.writeheader()
        writer.writerows(rows)
    write_profile_markdown(
        sheets, roles, scaled, scaled_encoding, label_granularity, label_reason, daily
    )
    print(f"KAMP label granularity: {label_granularity}")
    print(f"Wrote profile outputs to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
