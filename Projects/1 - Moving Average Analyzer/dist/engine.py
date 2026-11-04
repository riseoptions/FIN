"""Shared, causal moving-average research engine. Daily bars are canonical."""
import json, math
import numpy as np
import pandas as pd
from scipy.stats import norm

HORIZONS = [5, 10, 20, 40, 60]
DEFAULT = dict(tolerance=1.0, zone='percent', atr_mult=0.5, custom_floor=0.25,
               touch='range', min_touch=1, gap=3, side='both', confirm='zone',
               confirm_pct=1.0, confirm_bars=1, timeout=15, train=0.7,
               fee_bps=5, spread_bps=5, horizon=20, objective='combined',
               visual_weight=0.5, min_period=5, max_period=250, step=1,
               start='', end='', timeframe='daily', types=['SMA','EMA','WMA'])

def frame(records):
    d = pd.DataFrame(records).copy()
    d.columns = [str(c).lower().strip() for c in d.columns]
    need = ['date','open','high','low','close','volume']
    if not set(need).issubset(d.columns):
        raise ValueError('Vajalikud CSV veerud: Date,Open,High,Low,Close,Volume')
    d=d[need]
    d['date']=pd.to_datetime(d.date, errors='raise').dt.tz_localize(None)
    if d.date.duplicated().any(): raise ValueError('Korduvad kuupäevad pole lubatud')
    d=d.sort_values('date').reset_index(drop=True)
    for c in need[1:]: d[c]=pd.to_numeric(d[c],errors='raise')
    if not np.isfinite(d[need[1:]].to_numpy()).all(): raise ValueError('Puuduvad või lõpmatud hinnad')
    if (d[['open','high','low','close']]<=0).any().any() or (d.volume<0).any(): raise ValueError('Vigane hind või maht')
    if ((d.high+1e-8<d[['open','close','low']].max(axis=1)) | (d.low-1e-8>d[['open','close','high']].min(axis=1))).any():
        raise ValueError('OHLC hinnavahemik on vastuoluline')
    d['high']=d[['high','open','close']].max(axis=1)
    d['low']=d[['low','open','close']].min(axis=1)
    return d

def config(c):
    p={**DEFAULT,**c}
    for k in ['tolerance','atr_mult','custom_floor','confirm_pct','fee_bps','spread_bps']:
        p[k]=float(p[k])
        if not math.isfinite(p[k]) or p[k]<0: raise ValueError(k+' peab olema mittenegatiivne')
    for k in ['min_touch','gap','confirm_bars','timeout','horizon','min_period','max_period','step']:
        p[k]=int(p[k])
        if p[k]<1: raise ValueError(k+' peab olema vähemalt 1')
    if p['max_period']>500 or p['min_period']>p['max_period']: raise ValueError('Perioodivahemik peab jääma 1–500 vahele')
    if p['horizon'] not in HORIZONS: raise ValueError('Vigane horisont')
    if not .3<=float(p['train'])<=.9: raise ValueError('Treeningosa peab olema 30–90%')
    if not 0<=float(p['visual_weight'])<=1: raise ValueError('Kaal peab olema 0–1')
    for k,opts in dict(zone=['percent','atr','custom'],touch=['range','close'],side=['both','above','below'],confirm=['zone','percent'],objective=['visual','signals','combined'],timeframe=['daily','weekly']).items():
        if p[k] not in opts: raise ValueError('Tundmatu '+k)
    if not p['types'] or any(t not in ['SMA','EMA','WMA'] for t in p['types']): raise ValueError('Vigane MA tüüp')
    return p

def ma(s, kind, n):
    n=int(n)
    if n<1 or n>500: raise ValueError('MA periood peab olema 1–500')
    if kind=='SMA': return s.rolling(n,min_periods=n).mean()
    if kind=='EMA': return s.ewm(span=n,adjust=False,min_periods=n).mean()
    if kind=='WMA':
        w=np.arange(1,n+1,dtype=float)
        return s.rolling(n).apply(lambda x: np.dot(x,w)/w.sum(),raw=True)
    raise ValueError('Tundmatu MA tüüp')

def indicators(d, spec, p):
    # Weekly indicator uses ONLY previous completed weeks, available from next Monday.
    if p['timeframe']=='weekly':
        w=d.set_index('date').close.resample('W-FRI').last().dropna()
        v=ma(w,spec['type'],spec['period']); v.index=v.index+pd.Timedelta(days=3)
        m=v.reindex(pd.DatetimeIndex(d.date),method='ffill').reset_index(drop=True)
    else: m=ma(d.close,spec['type'],spec['period'])
    prev=d.close.shift()
    tr=pd.concat([d.high-d.low,(d.high-prev).abs(),(d.low-prev).abs()],axis=1).max(axis=1)
    atr=tr.rolling(14,min_periods=14).mean()
    width=m*p['tolerance']/100
    if p['zone']=='atr': width=atr*p['atr_mult']
    if p['zone']=='custom': width=pd.concat([m*p['tolerance']/100,atr*p['atr_mult'],pd.Series(p['custom_floor'],index=d.index)],axis=1).max(axis=1)
    return m, m-width, m+width

def events(d,m,lo,hi,p):
    touch=((d.low<=hi)&(d.high>=lo)) if p['touch']=='range' else ((d.close>=lo)&(d.close<=hi))
    closes=d.close.to_numpy(); lows=lo.to_numpy(); highs=hi.to_numpy(); touched=touch.to_numpy()
    date_strings=d.date.dt.strftime('%Y-%m-%d').tolist()
    touches=[]; signals=[]; pending=None; previous_side=0; last_touch=-100000; run=0; active=False
    for i in range(len(d)):
        if not np.isfinite(lows[i]) or not np.isfinite(highs[i]): continue
        side=1 if closes[i]>highs[i] else (-1 if closes[i]<lows[i] else 0)
        allowed=lambda s: p['side']=='both' or (p['side']=='above' and s==1) or (p['side']=='below' and s==-1)
        if touched[i]:
            if i-last_touch>p['gap']: active=False; run=0
            run+=1
            if not active and run>=p['min_touch'] and previous_side and allowed(previous_side):
                touches.append(dict(index=i,date=date_strings[i],side=previous_side))
                pending=dict(index=i,origin=previous_side,anchor=float(closes[i]),count=0,direction=0)
                active=True
            last_touch=i
        else: run=0
        # Gaps that jump through a whole zone are also breakouts; require known prior side.
        if not touched[i] and previous_side and side==-previous_side and pending is None and allowed(previous_side):
            pending=dict(index=i-1,origin=previous_side,anchor=float(closes[i-1]),count=0,direction=0)
        if pending and i>pending['index']:
            if i-pending['index']>p['timeout']: pending=None
            else:
                direction=side
                if p['confirm']=='percent' and direction*(closes[i]/pending['anchor']-1)*100<p['confirm_pct']: direction=0
                if direction:
                    pending['count']=pending['count']+1 if direction==pending['direction'] else 1
                else: pending['count']=0
                pending['direction']=direction
                if pending['count']>=p['confirm_bars']:
                    kind='bounce' if direction==pending['origin'] else 'breakout'
                    signals.append(dict(index=i,date=date_strings[i],direction=direction,kind=kind,
                        reason=('Põrge' if kind=='bounce' else 'Läbimurre')+(' üles' if direction>0 else ' alla')+'; kinnitus '+p['confirm']))
                    pending=None
        if side: previous_side=side
    return touches,signals

def stats(d,signals,start,end,h,p):
    rows=[]; busy_until=-1; eligible=0
    cost=(2*p['fee_bps']+p['spread_bps'])/10000
    for s in signals:
        i=s['index']; entry=i+1; out=entry+h-1
        if i<start or out>=end: continue
        eligible+=1
        if entry<=busy_until: continue
        busy_until=out
        price=float(d.open.iloc[entry]); direction=s['direction']; path=d.iloc[entry:out+1]
        gross=direction*(float(d.close.iloc[out])/price-1)
        adverse=(path.low.min()/price-1) if direction>0 else (1-path.high.max()/price)
        rows.append(dict(signal_date=s['date'],entry_date=str(d.date.iloc[entry].date()),exit_date=str(d.date.iloc[out].date()),
            direction=direction,kind=s['kind'],net=100*(gross-cost),mae=100*min(0,float(adverse)-cost)))
    values=[r['net'] for r in rows]; n=len(values); wins=sum(v>0 for v in values)
    if n:
        z=float(norm.ppf(.975)); q=wins/n; den=1+z*z/n; centre=(q+z*z/(2*n))/den
        radius=z*math.sqrt(q*(1-q)/n+z*z/(4*n*n))/den; ci=[100*(centre-radius),100*(centre+radius)]
    else: ci=[None,None]
    bh=100*(float(d.close.iloc[end-1])/float(d.open.iloc[start])-1-cost) if end>start else None
    return dict(n=n,eligible=eligible,mean=float(np.mean(values)) if n else None,median=float(np.median(values)) if n else None,
        win_rate=100*wins/n if n else None,win_ci=ci,mae=min((r['mae'] for r in rows),default=None),buy_hold=bh,trades=rows)

def bounds(d,p):
    mask=pd.Series(True,index=d.index)
    if p['start']: mask &= d.date>=pd.Timestamp(p['start'])
    if p['end']: mask &= d.date<=pd.Timestamp(p['end'])
    ids=np.flatnonzero(mask)
    if len(ids)<30: raise ValueError('Valitud ajavahemikus peab olema vähemalt 30 päevaküünalt')
    a=int(ids[0]); b=int(ids[-1])+1; split=a+int((b-a)*float(p['train']))
    return a,split,b

def analyze(d,spec,p,a,split,b,detail=True):
    m,lo,hi=indicators(d,spec,p); touches,signals=events(d,m,lo,hi,p)
    train={str(h):stats(d,signals,a,split,h,p) for h in (HORIZONS if detail else [p['horizon']])}
    test={str(h):stats(d,signals,split,b,h,p) for h in (HORIZONS if detail else [p['horizon']])} if detail else {}
    nt=sum(a<=x['index']<split for x in touches)
    # Penalize time spent inside the zone: a huge band is not automatically a good fit.
    occupancy=float(((d.close>=lo)&(d.close<=hi)).iloc[a:split].mean())
    visual=min(1,nt/max(1,(split-a)/20))*(1-occupancy)
    st=train[str(p['horizon'])]
    quality=(.5+.5*math.tanh((st['mean'] or 0)/3))*min(1,st['n']/10)
    weight=1 if p['objective']=='visual' else (0 if p['objective']=='signals' else float(p['visual_weight']))
    score=100*(weight*visual+(1-weight)*quality)
    r=dict(spec=spec,score=score,touch_count=nt,occupancy=occupancy,train=train,test=test)
    if detail:
        clean=lambda s:[float(v) if np.isfinite(v) else None for v in s]
        r.update(ma=clean(m.iloc[a:b]),lower=clean(lo.iloc[a:b]),upper=clean(hi.iloc[a:b]),
                 touches=[x for x in touches if a<=x['index']<b],signals=[x for x in signals if a<=x['index']<b])
    return r

def run(payload):
    p=config(payload.get('params',{})); d=frame(payload['prices']); a,split,b=bounds(d,p)
    specs=payload.get('specs',[dict(type='EMA',period=21,color='#53dfbc',width=2)])
    if not 1<=len(specs)<=12: raise ValueError('Kuva 1–12 keskmist')
    ranking=[]
    if payload.get('action')=='optimize':
        # Candidate search never receives test prices, including incomplete outcome windows.
        train_d=d.iloc[:split].copy()
        for kind in p['types']:
            for period in range(p['min_period'],p['max_period']+1,p['step']):
                spec=dict(type=kind,period=period,color='#f6c768',width=2)
                r=analyze(train_d,spec,p,a,split,split,False)
                if indicators(train_d,spec,p)[0].iloc[a:split].notna().sum()<20: continue
                ranking.append(r)
        ranking=sorted(ranking,key=lambda x:(-x['score'],x['spec']['period'],x['spec']['type']))[:5]
        if not ranking: raise ValueError('Liiga vähe andmeid valitud perioodidele; lühenda MA vahemikku')
        ranking=[analyze(d,r['spec'],p,a,split,b) for r in ranking]
    results=[analyze(d,s,p,a,split,b) for s in specs]
    return dict(schema_version='1.0',module='moving_average',symbol=payload.get('symbol','CSV'),source=payload.get('source',{}),
        params=p,split_date=str(d.date.iloc[split].date()),dates=[str(x.date()) for x in d.date.iloc[a:b]],
        prices=d.iloc[a:b].assign(date=lambda x:x.date.dt.strftime('%Y-%m-%d')).to_dict('records'),results=results,ranking=ranking,
        caveats=['Ajalooline sobivus ei tõenda tulevast tootlust.','Testperioodi korduv vaatamine muudab selle arendusandmeteks.'])

def bridge(raw): return json.dumps(run(json.loads(raw)),allow_nan=False)
