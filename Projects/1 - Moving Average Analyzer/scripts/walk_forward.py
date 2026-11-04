"""Expanding-window validation; each test segment is evaluated once."""
import json,sys,pathlib,argparse
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'dist'))
from engine import frame,config,analyze

def walk_forward(prices,initial=504,test_size=126,params=None):
    d=frame(prices);p=config(params or {});folds=[]
    for cut in range(initial,len(d)-test_size+1,test_size):
        td=d.iloc[:cut];rank=[]
        for kind in p['types']:
            for n in range(p['min_period'],p['max_period']+1,p['step']):
                s=dict(type=kind,period=n)
                rank.append(analyze(td,s,p,0,cut,cut,False))
        best=max(rank,key=lambda r:r['score'])
        r=analyze(d.iloc[:cut+test_size],best['spec'],p,0,cut,cut+test_size)
        folds.append(dict(train_end=str(d.date.iloc[cut-1].date()),test_start=str(d.date.iloc[cut].date()),test_end=str(d.date.iloc[cut+test_size-1].date()),spec=r['spec'],train=r['train'],test=r['test']))
    return folds
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('file');p.add_argument('--output',default='walk-forward.json');a=p.parse_args()
    data=json.loads(pathlib.Path(a.file).read_text());r=walk_forward(data['prices'],params=dict(min_period=5,max_period=100,step=5))
    pathlib.Path(a.output).write_text(json.dumps(r,indent=2));print(len(r),'folds ->',a.output)
