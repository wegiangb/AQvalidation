"""Modern, reproducible baseline runner; original milestone scripts remain unchanged.
Offline: python run_milestones.py --csv path/to/file.csv
Live: OPENAQ_API_KEY=... python run_milestones.py --sensor-id 123 --date-from 2025-01-01 --date-to 2025-01-31
"""
import argparse, json, os, pathlib, sys
import numpy as np
import pandas as pd
import requests

def fetch(sensor_id, start, end):
    key=os.getenv('OPENAQ_API_KEY')
    if not key: raise RuntimeError('OPENAQ_API_KEY is required for live downloads')
    rows=[]; page=1
    while True:
        response=requests.get(f'https://api.openaq.org/v3/sensors/{sensor_id}/hours',headers={'X-API-Key':key},params={'datetime_from':start,'datetime_to':end,'limit':1000,'page':page},timeout=35)
        response.raise_for_status(); payload=response.json(); chunk=payload.get('results',[])
        if not chunk: break
        for r in chunk:
            dt=r.get('period',{}).get('datetimeFrom',{}).get('utc') or r.get('datetime',{}).get('utc')
            rows.append({'location':f'sensor:{sensor_id}','parameter':str(sensor_id),'value':r.get('value'),'date.utc':dt,'unit':'unknown','coordinates.latitude':np.nan,'coordinates.longitude':np.nan})
        if len(chunk)<1000: break
        page+=1
        if page>100: raise RuntimeError('Safety limit of 100 pages reached; narrow date range')
    return pd.DataFrame(rows)

def run(df,out):
    out.mkdir(parents=True,exist_ok=True)
    required={'location','parameter','value','date.utc'}
    if not required.issubset(df.columns): raise ValueError('Missing columns: '+str(required-set(df.columns)))
    df=df.copy(); df['date.utc']=pd.to_datetime(df['date.utc'],utc=True,errors='coerce');df['value']=pd.to_numeric(df['value'],errors='coerce')
    df=df.dropna(subset=['date.utc']); df.to_csv(out/'milestone1_observations.csv',index=False)
    results=[]
    for (station,parameter),g in df.groupby(['location','parameter'],dropna=False):
        g=g.sort_values('date.utc'); values=g['value']; valid=values.dropna(); n=len(g)
        # Hourly coverage is meaningful only when input is hourly or near-hourly.
        hours=g['date.utc'].dt.floor('h').nunique(); span=int((g['date.utc'].max()-g['date.utc'].min()).total_seconds()/3600)+1
        hourly=bool(len(g)>1 and g['date.utc'].diff().dropna().median()<=pd.Timedelta(hours=2))
        coverage=round(hours/span,4) if hourly and span else None
        median=float(valid.median()) if len(valid) else None
        mad=float((valid-valid.median()).abs().median()) if len(valid) else None
        outliers=int(((values-median).abs()>6*1.4826*mad).sum()) if mad and mad>0 else 0
        negatives=int((values<0).sum());missing=int(values.isna().sum());duplicates=int(g['date.utc'].duplicated().sum())
        quality='review' if missing or negatives or duplicates or outliers else 'pass'
        suitable=bool(quality=='pass' and coverage is not None and coverage>=.75 and n>=24)
        results.append({'station':str(station),'pollutant':str(parameter),'observations':n,'start_utc':str(g['date.utc'].min()),'end_utc':str(g['date.utc'].max()),'hourly_coverage':coverage,'missing_values':missing,'negative_values':negatives,'duplicate_timestamps':duplicates,'robust_outliers':outliers,'median':median,'mad':mad,'qc_status':quality,'temporal_comparison_candidate':suitable,'representativeness':'not_assessed_requires_geospatial_context'})
    report=pd.DataFrame(results)
    report.to_csv(out/'milestone2_station_reliability.csv',index=False)
    report[['station','pollutant','missing_values','negative_values','duplicate_timestamps','robust_outliers','qc_status']].to_csv(out/'milestone3_qc_summary.csv',index=False)
    report[['station','pollutant','temporal_comparison_candidate','representativeness']].to_csv(out/'milestone4_classification_preliminary.csv',index=False)
    summary={'stations_pollutant_pairs':len(report),'observations':len(df),'qc_pass':int((report.qc_status=='pass').sum()),'temporal_candidates':int(report.temporal_comparison_candidate.sum()),'limitations':['Baseline QC is not Pecos; original Pecos checks not yet migrated','Highway distance and spatial representativeness not evaluated','Hourly completeness is only calculated for near-hourly series','Live OpenAQ results require API key; sensor metadata/units must be enriched before scientific comparison']}
    (out/'run_summary.json').write_text(json.dumps(summary,indent=2));return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--csv');p.add_argument('--sensor-id',type=int);p.add_argument('--date-from');p.add_argument('--date-to');p.add_argument('--out',default='run_output');a=p.parse_args()
    if a.csv: df=pd.read_csv(a.csv)
    elif a.sensor_id and a.date_from and a.date_to: df=fetch(a.sensor_id,a.date_from,a.date_to)
    else: p.error('Supply --csv or --sensor-id with --date-from and --date-to')
    print(json.dumps(run(df,pathlib.Path(a.out)),indent=2))
if __name__=='__main__':main()
