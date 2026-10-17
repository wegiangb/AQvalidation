# Modern baseline runner (initial test)

The historical scripts are unchanged. `run_milestones.py` is a new **baseline** pipeline, not a complete implementation of the four original milestones.

## Setup

`python -m pip install pandas numpy requests`

## Offline run

`python run_milestones.py --csv 'Milestone1_Importing-datasets-from-OpenAQ/OpenAQ_Dataset Unique selection pm25 One Station 2020-03-01 to 2020-09-01.csv' --out output`

## Live OpenAQ v3 (requires API key)

Set `OPENAQ_API_KEY` securely in your shell, then:

`python run_milestones.py --sensor-id SENSOR_ID --date-from 2025-01-01 --date-to 2025-01-31 --out output`

Live output currently labels parameter with sensor ID, does not fetch unit/station metadata, and therefore is **not** comparison-ready. Review API pagination, date parameter support and data semantics before production use.

## Outputs

- milestone1_observations.csv — input normalized to timestamps/numeric values
- milestone2_station_reliability.csv — preliminary station-level diagnostics
- milestone3_qc_summary.csv — baseline flags (not Pecos)
- milestone4_classification_preliminary.csv — temporal candidate and representativeness unknown (not highway classification)
- run_summary.json — run totals and limitations

## Outstanding

Migrate original Pecos rules and threshold YAMLs; implement nearest-road distance using current geospatial services; enrich OpenAQ metadata; make period-by-period QC and pollutant-specific thresholds; test with API credentials and multiple live sensors. Results are diagnostic, not scientific validation.
