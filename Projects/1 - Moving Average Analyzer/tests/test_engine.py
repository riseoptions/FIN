import sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'dist'))
import numpy as np
import pandas as pd
import pytest
from engine import *

def sample(n=500):
    c=100+np.arange(n)*.03+5*np.sin(np.arange(n)/7)
    return pd.DataFrame(dict(date=pd.bdate_range('2020-01-01',periods=n),open=c,high=c+1,low=c-1,close=c,volume=1000))

def test_means():
    s=pd.Series([1.,2.,3.,4.])
    assert ma(s,'SMA',3).iloc[-1]==3
    assert ma(s,'WMA',3).iloc[-1]==pytest.approx(20/6)
    assert ma(s,'EMA',3).iloc[-1]==pytest.approx(3.125)
    assert ma(s,'SMA',3).iloc[:2].isna().all()

def test_zones():
    d=sample();p=config({});m,lo,hi=indicators(d,dict(type='SMA',period=5),p)
    assert hi.iloc[-1]==pytest.approx(m.iloc[-1]*1.01)
    assert lo.iloc[-1]==pytest.approx(m.iloc[-1]*.99)
    p['zone']='atr';_,lo,hi=indicators(d,dict(type='SMA',period=5),p)
    assert hi.iloc[-1]-lo.iloc[-1]>0

def test_prefix_causality():
    d=sample();p=config({});s=dict(type='EMA',period=21)
    full=events(d,*indicators(d,s,p),p)
    small=d.iloc[:300];prefix=events(small,*indicators(small,s,p),p)
    for a,b in zip(full,prefix): assert [x for x in a if x['index']<300]==b

def test_train_invariance():
    d=sample();payload=dict(prices=d.assign(date=d.date.dt.strftime('%Y-%m-%d')).to_dict('records'),action='optimize',params=dict(min_period=5,max_period=20,step=5))
    r=run(payload);d.loc[350:,['open','high','low','close']]*=4
    payload['prices']=d.assign(date=d.date.dt.strftime('%Y-%m-%d')).to_dict('records');other=run(payload)
    assert [(x['spec'],x['score']) for x in r['ranking']]==[(x['spec'],x['score']) for x in other['ranking']]

def test_execution_cost_overlap_boundary():
    d=sample(100);p=config(dict(fee_bps=10,spread_bps=10));ss=[dict(index=i,date=str(d.date.iloc[i].date()),direction=1,kind='bounce') for i in [10,11,15,48]]
    s=stats(d,ss,0,50,5,p)
    assert s['n']==2 and s['eligible']==3
    assert s['trades'][0]['entry_date']==str(d.date.iloc[11].date())
    assert s['trades'][0]['net']==pytest.approx(100*(d.close.iloc[15]/d.open.iloc[11]-1-.003))
    assert s['mae']<=0

def test_weekly_no_future():
    d=sample(60);p=config(dict(timeframe='weekly'));spec=dict(type='SMA',period=2)
    cut=43;full=indicators(d,spec,p)[0];part=indicators(d.iloc[:cut],spec,p)[0]
    np.testing.assert_allclose(full.iloc[:cut],part,equal_nan=True)

def test_signal_types_and_grouping():
    c=[103,101,100,100,103,104,101,100,97,96,99,100,103,104,99,100,97]
    d=pd.DataFrame(dict(date=pd.bdate_range('2020-01-01',periods=len(c)),open=c,close=c,high=np.array(c)+.1,low=np.array(c)-.1,volume=1))
    m=pd.Series(100.,index=d.index);p=config(dict(gap=1))
    t,s=events(d,m,m-1,m+1,p)
    assert len(t)==4
    assert {(x['kind'],x['direction']) for x in s}=={('bounce',1),('breakout',-1),('breakout',1)}
    assert s[0]['index']==4

def test_validation_and_empty():
    d=sample(50);d.loc[0,'low']=200
    with pytest.raises(ValueError): frame(d.to_dict('records'))
    with pytest.raises(ValueError): config(dict(max_period=999))
    d=sample(50);s=stats(d,[],0,50,20,config({}));assert s['n']==0 and s['mean'] is None

def test_down_bounce_and_confirmation():
    c=[97,100,99,97,96]
    d=pd.DataFrame(dict(date=pd.bdate_range('2020-01-01',periods=5),open=c,close=c,high=np.array(c)+.1,low=np.array(c)-.1,volume=1))
    m=pd.Series(100.,index=d.index)
    _,s=events(d,m,m-1,m+1,config(dict(confirm_bars=2)))
    assert len(s)==1 and s[0]['kind']=='bounce' and s[0]['direction']==-1 and s[0]['index']==4

def test_min_touch_and_side_filter():
    d=sample(100);p=config(dict(side='above',min_touch=2,gap=5));t,s=events(d,*indicators(d,dict(type='SMA',period=5),p),p)
    assert all(x['side']==1 for x in t)
    assert all(b['index']-a['index']>5 for a,b in zip(t,t[1:]))

def test_walk_forward_boundary():
    sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
    from walk_forward import walk_forward
    d=sample(300);r=walk_forward(d.to_dict('records'),initial=150,test_size=75,params=dict(min_period=5,max_period=10,step=5))
    assert len(r)==2
    for f in r:
        assert f['train_end']<f['test_start']
        for h in HORIZONS:
            assert all(f['test_start']<=t['signal_date']<t['entry_date']<=t['exit_date']<=f['test_end'] for t in f['test'][str(h)]['trades'])
