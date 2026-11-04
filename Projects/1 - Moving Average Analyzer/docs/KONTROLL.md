# Kontrolliaruanne — 4. november 2026

## Automatiseeritud kontroll

`python -m pytest -q`: **11 testi läbitud**.

- SMA, EMA ja WMA käsitsi arvutatavate väärtuste võrdlus.
- Protsendi- ja ATR-tsooni piirid.
- Signaalide invariantsus tulevaste ridade lisamisel.
- TOP 5 ja treeningskoori invariantsus testihindade muutmisel.
- Järgmise päeva avahind, kulud, kattuvate tehingute välistamine ja valimi lõpp.
- Nädalase MA tulevikuinfo vältimine.
- Ülespõrge ja mõlemasuunalised läbimurded, sündmuste liitmine.
- OHLC valideerimine ja tühi signaalivalim.
- Allapõrge kahe kinnituspäevaga.
- Lähenemissuund ja puutevahe.
- Walk-forward tehingute paiknemine ainult oma testiaknas.

`node --check dist/app.js` ja `node --check dist/worker.js`: läbitud.

Kohalik täielik 738 kandidaadi otsing (SMA/EMA/WMA, perioodid 5–250) AAPL-i 2025-11-03…2026-11-03 vahemikus: ligikaudu 8,45 sekundit selles keskkonnas. TOP 5: SMA18, WMA24, SMA14, SMA17, SMA13. See on reprodutseeritav kontrollnäide, mitte soovitus neid parameetreid kasutada.

## Brauseris kontrollitud

- Pärisandmete laadimine, Pyodide käivitumine ja Plotly graafik.
- Täielik 738 kandidaadi otsing: sama TOP 5 kui kohalikus Pythonis.
- Automaattulemuse taastamine: kaks parimat keskmist graafikul.
- Tolerantsi muutmine 1 → 1,4 ja uus statistika.
- Seadistuse brauserisse salvestamine.
- JSON-seadistuse allalaadimine ja sama faili importimine.
- AAPL, MSFT ja NVDA normaliseeritud hinnavõrdlus.
- Nädalagraafik ja muutunud nädalaste MA-de statistika.

CSV valideerimine on kaetud Pythoni testidega ja kaasas on pärisandmetega CSV näited. Kõiki võimalikke kasutaja CSV murdeid ega kõiki brausereid pole testitud.

## Andmed ja märkmik

AAPL, MSFT ja NVDA: igaühel 2512 päevaküünalt, viimane 2026-11-03. Allikas Yahoo Finance/yfinance; korrigeeritud OHLC. Näiteskript käivitatud kõigile kolmele sümbolile. Colabi märkmiku koodisüntaks kontrollitud ja algoritmilised osad (sh 4 walk-forward-akent) kohalikus Pythonis käivitatud. Google'i Colabi üleslaadimisliidest selles keskkonnas ei avatud.

## Avaldamise piir

Sama `dist` on staatiliselt majutatav GitHub Pagesis. Pagesi töövoog on kaasas; kasutaja GitHubi hoidlas pole töövoogu käivitatud ega sealset URL-i kontrollitud, sest hoidla ühendus puudub. Eraldi avaldatud veebiversiooni URL antakse projekti üleandmisel. Ajastatud hindade uuendus rakendub GitHubis alles pärast töövoo lubamist; eraldi veebiversioon kasutab kaasasolevat hinnapilti.
