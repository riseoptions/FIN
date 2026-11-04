"""Run locally, in Colab or GitHub Actions. Never substitutes synthetic data."""
import argparse, json, re, pathlib, sys
from datetime import datetime, timezone
import yfinance as yf
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'dist'))
from engine import frame

def download(symbol,output):
    symbol=symbol.upper().strip()
    if not re.fullmatch(r'[A-Z0-9^][A-Z0-9.^-]{0,14}',symbol): raise ValueError('Vigane sümbol')
    d=yf.Ticker(symbol).history(period='10y',auto_adjust=True,actions=False)
    if d.empty: raise ValueError(symbol+': andmeallikas ei tagastanud hindu')
    d=d.reset_index(); d.columns=[str(x).lower() for x in d.columns]
    d['date']=d.date.dt.strftime('%Y-%m-%d')
    records=frame(d.to_dict('records')).assign(date=lambda x:x.date.dt.strftime('%Y-%m-%d')).to_dict('records')
    result=dict(schema_version='1.0',symbol=symbol,source=dict(provider='Yahoo Finance / yfinance',adjustment='auto_adjust=True; split- ja dividendikorrigeeritud OHLC',updated_at=datetime.now(timezone.utc).isoformat(),last_date=records[-1]['date'],synthetic=False),prices=records)
    output.mkdir(parents=True,exist_ok=True)
    path=output/(symbol+'.json'); path.write_text(json.dumps(result),encoding='utf-8')
    print(symbol,len(records),records[-1]['date'])
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--symbols',default='AAPL,MSFT,NVDA'); p.add_argument('--output',default='dist/data'); args=p.parse_args()
    for s in args.symbols.split(','): download(s,pathlib.Path(args.output))
