# GitHub Actions setup

1. Copy these files into the repository root, preserving `.github/workflows/air-quality-validation.yml`.
2. GitHub repository → Settings → Secrets and variables → Actions → New repository secret: `OPENAQ_API_KEY`.
3. GitHub → Actions → Air quality validation → Run workflow.
4. First leave `sensor_ids` blank to run offline tests. Then supply actual OpenAQ v3 **sensor** IDs (not location IDs), separated by commas, and dates.
5. Download `air-quality-validation-reports` from the completed workflow run.

The workflow runs offline tests on pushes and pull requests; live API requests only happen on manual dispatch with sensor IDs. The API key is never written to reports. Avoid adding secrets to issue descriptions or workflow inputs.

**Scientific limitation:** This workflow executes the modern baseline runner. Milestone 3 is NOT yet original Pecos QC; milestone 4 does NOT yet compute road proximity or station representativeness. These CSVs are preliminary and must not be treated as completed scientific validation. Live OpenAQ sensor metadata, pollutant identity and units remain unenriched in the baseline runner. The workflow will fail if API credentials or requested sensor IDs are invalid.
