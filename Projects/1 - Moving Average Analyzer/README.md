# Moving Average Analyzer — Turulabor 01/06

Eestikeelne staatiline veebirakendus USA aktsiate libisevate keskmiste uurimiseks. Üks ja sama Pythoni arvutusmootor töötab brauseri Web Worker'is Pyodide'iga, kohalikus Pythonis ja Colabis. Serverit, API võtit ega tasulist teenust pole vaja.

## Kiire algus

1. Paki projekt lahti.
2. Ava terminal projekti kaustas ja käivita `python -m http.server 8000 --directory dist`.
3. Ava **http://localhost:8000**. Ära ava HTML-i `file://` kaudu: Worker ja hinnapäringud vajavad HTTP-d.
4. Esmakäivitus laadib Pyodide'i ning NumPy, Pandase ja SciPy. Vaja on internetiühendust; arvuti enda Pythonit veebilehe kasutamiseks ei vajata.
5. Vali AAPL, MSFT või NVDA. Kaasas on tegelikud Yahoo Finance'i korrigeeritud päevahinnad; viimane kuupäev ja laadimisaeg on iga andmefaili `source` väljal.

## Kasutamine

- Ajavahemik: 3/6 kuud, 1/3/5 aastat või algus- ja lõppkuupäev. Periood arvutatakse viimase saadaoleva hinnapäeva suhtes.
- SMA, EMA ja WMA: lisa kuni 12 joont, muuda perioodi, värvi ja paksust. Periood on päevagraafikul päevades, nädalagraafikul nädalates.
- Puutetsoon: protsent keskmisest; 14 päeva ATR × kordaja; kohandatud `max(protsendilaius, ATR-laius, dollaripõrand)`.
- Puude: sulgemine tsoonis või päeva High/Low kattumine tsooniga. Määra järjestikused päevad, sündmuste vahe ja lähenemise suund.
- Kinnitus: sulgemine tsoonist väljas või lisaks nõutav suunaline protsendiliikumine puute registreerimise hinnast; võimalik mitu kinnituspäeva ja aegumine.
- Automaatotsing otsib kolme MA tüübi perioode. TOP 5 järjestatakse treeningu järgi. Lisa kandidaadid graafikule; statistika rippmenüü võimaldab kiiret võrdlust.
- „Taasta automaatne tulemus” taastab viimase otsingu parameetrid ja kaks parimat joont.
- „Salvesta seadistus” salvestab brauserisse; JSON eksport/import võimaldab liigutada seadistusi arvutite vahel. Hinnaandmed tuleb teises brauseris vajadusel uuesti importida.
- Tulemuste eksport sisaldab parameetreid, signaale, põhjendusi, hindu ning iga horisondi tehinguid.
- Aktsiate võrdlus normaliseerib ühisel ajavahemikul hinnad väärtusele 100. See on hinnavõrdlus, mitte optimeeritud strateegiate portfell.

## Vabalt sisestatud sümbolid ja CSV

Staatiline leht proovib `data/SYMBOL.json`. Suvaliste sümbolite jaoks on kaks töötavat teed:

```bash
pip install -r requirements.txt
python scripts/update_data.py --symbols TSLA,AMD
```

Seejärel sisesta lehel sümbol ja vajuta „Laadi”. Või impordi CSV (sümbol sisesta enne importi):

```csv
Date,Open,High,Low,Close,Volume
2025-01-02,100,102,99,101,1000000
```

See üks rida illustreerib ainult failivormingut. Analüüs vajab vähemalt 30 rida ja pikk MA piisavat eelajalugu. Kaasasolevad `examples/AAPL.csv`, `MSFT.csv`, `NVDA.csv` on pärisandmed. Kasuta kogu failis ühesugust korrigeerimist: ära sega korrigeeritud Close'i korrigeerimata OHLC-ga. Import kontrollib kuupäevi, duplikaate, arvväärtusi ja OHLC loogikat. Kuni 1e-8 hinnavahemiku ümardusviga normaliseeritakse.

Andmeid ei asendata tõrke korral sünteetilise hinnaseeriaga. Yahoo katkestuste või piirangute korral kasuta enda CSV-d. Yahoo/yfinance pole börsi ametlik reaalajavoog; andmete kasutamisel ja levitamisel kontrolli allika kasutustingimusi. Uuenduse ebaõnnestumisel säilib varasem andmefail ning kuupäev näitab selle vanust.

## GitHub Pages: avaldamine

1. Loo GitHubis hoidla, näiteks `moving-average-analyzer`.
2. Laadi **ZIP-i sisu**, mitte ZIP ise, hoidla juurkausta. Säilita `.github/workflows/pages.yml`. Paljude failide jaoks kasuta Git'i või GitHub Desktopi.
3. Vali **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Hoidla põhiharu peab olema `main` (või muuda töövoo harunime).
5. Vali **Actions → Test, update prices and publish Pages → Run workflow**.
6. Töövoog käivitab testid, proovib värskendada hindu, pakib projekti ja avaldab `dist` kausta. Valmis aadress ilmub töövoo Deploy etapi väljundisse.
7. Uuendus on ajastatud E–R kell 23:30 UTC. Actionsi ajastus ei garanteeri täpset käivitumisaega. Sümboleid saab käsitsi käivitusel muuta.

Uuendused avaldatakse lehele töövoo artefaktist; neid ei kirjutata automaatselt tagasi Git'i. Uus sümbol püsib avaldatud versioonis kuni järgmise avaldamiseni — lisa püsiv sümbol skripti/töövoo vaikimisi loendisse või hoidlasse. Pagesi tegelik avaldamine sinu kontol nõuab sinu hoidlat ja selle ligipääsu. Projekti koostamise ajal kontrolliti sama staatilist rakendust eraldi veebimajutuses; sinu GitHubi kontol pole hoidlat loodud.

## Python, Thonny ja Colab

```bash
pip install -r requirements.txt
python -m pytest -q
python scripts/walk_forward.py dist/data/AAPL.json --output walk-forward.json
```

Thonnys vali **Tools → Manage packages**, paigalda requirements.txt teegid ja ava `examples/analyze.py`. Colabis ava `notebooks/01_optimeerimine.ipynb` ning laadi sinna projekti ZIP. Märkmik sisaldab seletusi, graafikut ja iseseisvat katset koos vastuse suunisega.

## Struktuur ja järgmised moodulid

```text
dist/engine.py          — puhas Pythoni arvutusliides, UI-st sõltumatu
dist/worker.js          — Pyodide ja JSON sõnumid
dist/app.js             — kasutajaliides ja Plotly
dist/data/             — ühised päevahinnad ja päritolu
scripts/update_data.py — Yahoo → valideeritud hinnad
scripts/walk_forward.py— ajas edasi liikuv sõltumatu test
scripts/package.py     — allalaaditava lähtekoodipaketi ehitamine
tests/                 — matemaatika, põhjuslikkus, piirid
notebooks/             — Colabi õppenäide
docs/                  — metoodika ja moodulite andmeleping
```

Vaata [metoodikat](docs/METOODIKA.md), [andmelepingut](docs/ANDMELEPING.md) ja [kontrolliaruannet](docs/KONTROLL.md). Options IV, News Sentiment, Analyst Ratings, Fundamental ja Geopolitical Impact lisavad oma arvutusmooduli, kuid kasutavad sama `symbol`, `source`, `prices` ja versiooniga tulemuse ümbrist. Praeguses rakenduses pole neid viit moodulit ega LLM-i veel teostatud.

## Piirangud

See on kontrollitav sündmusuuring, mitte tootmiskõlblik kauplemissüsteem. Tehingud on ühe aktsia fikseeritud horisondi suunapositsioonid ilma positsioonide liitmise, kapitalipiirangute, maksude, intressi, lühikeseks müügi laenukulu, turumõju ja marginaalikutseteta. Kulu on `2 × tasu + spread`. ATR arvutatakse lihtsa 14 päeva keskmisena, mitte Wilderi silumisena. Nädalane MA rakendub alles järgmisest esmaspäevast; see on konservatiivne ajastus ka pühadenädalatel. Viimane nädalaküünal võib olla pooleli.

Ühe testperioodi korduv kasutamine parameetrite muutmiseks kaotab selle sõltumatuse. Väikesed valimid ja paljude kandidaatide otsing võivad anda juhuslikke „võitjaid”. Wilsoni 95% osakaaluvahemik on kirjeldav ega kõrvalda aegridade sõltuvust. Walk-forward on Pythoni/Colabi töövoos, mitte veebilehe nupuna.

## Tehnilised allikad

- [Pyodide kasutamine](https://pyodide.org/en/stable/usage/index.html)
- [yfinance hinnapäringu API](https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html)
- [GitHub Pages kohandatud töövood](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

Teegid: Pyodide 0.27.7, Plotly 2.35.2, Papa Parse 5.4.1. Brauseris on need versioonid fikseeritud CDN URL-ides. Pythoni sõltuvuste versioonipiirid on requirements.txt failis.
