# Moodulite ühine andmeleping v1.0

Kõik kuupäevad on ISO `YYYY-MM-DD` börsipäeva sildid. `updated_at` on UTC ajatempli ISO string. Päevasiseseid tehinguaegu ei oletata. Hindade valuuta on selles moodulis USD; teiste valuutade lisamisel tuleb lisada `currency` ja ümberarvestuse päritolu.

```json
{
  "schema_version": "1.0",
  "symbol": "AAPL",
  "source": {
    "provider": "Yahoo Finance / yfinance",
    "adjustment": "auto_adjust=True",
    "updated_at": "2026-11-04T00:00:00+00:00",
    "last_date": "2026-11-03",
    "synthetic": false
  },
  "prices": [
    {"date": "2026-11-03", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000}
  ]
}
```

Ülal olevad hinnanumbrid on skeemi näide, mitte AAPL tegelik hind. Pärisandmed asuvad `dist/data` all.

`engine.run(payload)` võtab `prices`, `symbol`, `source`, `params`, `specs` ning `action=analyze|optimize`. Tagastus sisaldab `schema_version`, `module=moving_average`, sisendi päritolu ja parameetreid, `split_date`, nähtavaid hindu, `results` ning `ranking`.

Ühe tulemuse väljad:

| Väli | Sisu |
|---|---|
| spec | type, period, color, width |
| ma, lower, upper | dates pikkusega massiivid; puuduv väärtus null |
| touches | index (algse päevase andmerea indeks), date, side |
| signals | index, date, direction, kind, reason |
| train, test | horisondid võtmetena 5,10,20,40,60 |
| n, eligible | tehingute ja täieliku tulevikuga signaalide arv |
| mean, median, win_rate, mae, buy_hold | protsendipunktides arvud; tühi valim null |
| trades | tegelikud sisenemise/väljumise kuupäevad, direction, kind, net, mae |

Järgmine moodul peab tagastama oma `module` nime ja sama päritoluümbrise. Hoia hinnalaadimine ühine, kuid ära pane uudise või optsioonilepingu andmeid OHLCV ritta. Lisa moodulile oma `inputs` ja `results`. Laiendamisel muuda lepingu versiooni, kui olemasoleva välja tähendus muutub. Uudistel peab olema avaldamisaeg, optsioonidel alusvara, aegumine ja strike. Kõik ühendavad analüüsid peavad kasutama ainult otsuse hetkeks avaldatud infot.
