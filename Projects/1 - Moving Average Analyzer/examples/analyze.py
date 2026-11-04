import sys,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dist'))
from engine import run
for symbol in ['AAPL','MSFT','NVDA']:
    data=json.loads((ROOT/'dist/data'/f'{symbol}.json').read_text())
    result=run({**data,'action':'optimize','params':{'min_period':5,'max_period':100,'step':5,'start':data['prices'][-756]['date']}})
    best=result['ranking'][0]
    print(symbol,best['spec'],'train',best['train']['20']['mean'],'test',best['test']['20']['mean'])
