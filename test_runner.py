import tempfile
import unittest
from pathlib import Path
import pandas as pd
from run_milestones import run

class RunnerSmokeTests(unittest.TestCase):
    def test_pipeline_outputs(self):
        df = pd.DataFrame({
            'location': ['test_station']*48,
            'parameter': ['pm25']*48,
            'date.utc': pd.date_range('2025-01-01', periods=48, freq='h', tz='UTC').astype(str),
            'value': [10.0]*48,
        })
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            summary=run(df,output)
            self.assertEqual(summary['observations'],48)
            self.assertEqual(summary['stations_pollutant_pairs'],1)
            for filename in ('milestone1_observations.csv','milestone2_station_reliability.csv','milestone3_qc_summary.csv','milestone4_classification_preliminary.csv','run_summary.json'):
                self.assertTrue((output/filename).exists())
            self.assertTrue(pd.read_csv(output/'milestone2_station_reliability.csv').iloc[0]['temporal_comparison_candidate'])

if __name__=='__main__': unittest.main()
