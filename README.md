# RISE MARKETS – FIN GitHub Pages

**GitHub:** https://github.com/riseoptions/FIN

## Variant A – uus turuleht FIN-i avaleheks (soovitatud)

1. Ava repositoorium `riseoptions/FIN` → **Code**.
2. Laadi siit pakist **index.html** ja **options.html** repositooriumi **juurkausta** (`/`, mitte `WEB/`).
3. Olemasolev `index.html` tuleb üle kirjutada / uuega asendada. `options.html` on senine optsioonikalkulaator eraldi lehena.
4. Veendu, et **Settings → Pages → Deploy from a branch → main → /(root)**.
5. Avaleht: https://riseoptions.github.io/FIN/
6. Senine optsioonikalkulaator: https://riseoptions.github.io/FIN/options.html

**Kui oled oma praegust optsioonikalkulaatorit muutnud, varunda vana `index.html` enne asendamist.** Fail `options.html` on siin varem koostatud OptionLabi versioon.

## Variant B – säilita praegune avaleht

Laadi repositooriumi juurkausta **markets.html** (selle leiad eraldi allalaadimislingilt).

- Senine avaleht jääb: https://riseoptions.github.io/FIN/
- Uus turuleht on: https://riseoptions.github.io/FIN/markets.html
- Turulehe navigeerimislink „Optsioonikalkulaator” viib praegusele avalehele.

## Kuidas see töötab?

- **HTML, CSS ja JavaScript:** kasutajaliides, päringud ja SVG-graafik.
- **Pyodide 0.29.5:** laetakse CDN-ist; Python standardteegiga arvutab päevatootluse, annualiseeritud ajaloolise volatiilsuse ja maksimaalse languse.
- **Hinnad:** mitteametliku Yahoo Finance chart-endpoint'i andmed `proxy.cors.dev` vahendusel, sest Yahoo ei luba brauserist otsepäringut (CORS).
- **Sümboli otsing:** näiteks `AAPL`, `TSLA`, `MSFT`, `SPY`, `^GSPC`, `^IXIC`, `BTC-USD`.
- **Värskendamine:** käsitsi „Värskenda”; sama sümboli ja perioodi päringud hoitakse 60 sekundit brauseris mälus.
- **Kuupäev:** kuvatakse andmeallikast saadud viimase hinna ajatempel Eesti ajas.

## Piirangud ja usaldusväärsus

1. Hinnad ei pruugi olla reaalajas; viivitus sõltub börsist ja andmeallikast. Ära kasuta kauplemiskorralduste tegemiseks.
2. `proxy.cors.dev` on **kolmanda osapoole vahendaja**. API on mitteametlik ja teenust võidakse piirata või muuta; 429/503, CORS-tõrked ning puuduvad hinnad on võimalikud. Kui andmeid ei tule, näitab leht selget viga, mitte väljamõeldud hindasid.
3. Külastaja brauseril peab olema internetiühendus, et Pyodide ja turuandmed laadida. Eriti esmakordsel avamisel võib Pythoni laadimine võtta aega.
4. JavaScript saadab sümbolipäringud vahendajale; ära sisesta API-võtmeid või saladusi lehe koodi.
5. Hinnagraafik kasutab päevaseid **kohandamata** sulgemishindu. Splittide ja dividendide mõju ei ole eemaldatud; ajaloolise tootluse ja riski arvutused on seetõttu indikatiivsed.

## Testid

- JavaScripti süntaks kontrollitud Node.js-iga.
- Python-statistika kontrollitud CPythoniga.
- Kasutajaliides, sümboliotsing ja perioodivahetus testitud Chromiumi brauseris **testandmete ja vahenduse simulatsiooniga**.
- Välist Yahoo/CORS teenust ja tegelikku Pyodide CDN-ist laadimist ei saanud selles keskkonnas lõpuni kontrollida; toimimine avalikus internetis sõltub välisteenustest.

## Õppeprojekt

Loodud hariduslikuks kasutuseks. Ei ole investeerimissoovitus.
