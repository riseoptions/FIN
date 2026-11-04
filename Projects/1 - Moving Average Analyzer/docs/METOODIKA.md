# Arvutusmetoodika

## Keskmised

- SMA(n): viimase n sulgemishinna aritmeetiline keskmine.
- EMA(n): `alpha=2/(n+1)`, rekursioon `EMA[t]=alpha*C[t]+(1-alpha)*EMA[t-1]`. Algväärtus on esimene sulgemine; enne n vaatlust tulemust ei kuvata (`adjust=False`).
- WMA(n): vanim kaal 1 ja uusim n; jagaja `n(n+1)/2`.
- ATR(14): `max(H-L, abs(H-eelmine C), abs(L-eelmine C))` viimase 14 päeva lihtne keskmine.

Graafikule eelnev ajalugu on keskmiste soojendus. Päevase signaali puhul võib MA sisaldada sama päeva sulgemist, sest signaal tekib alles päeva lõpus. Tehing algab järgmise päeva avamisel.

Nädalane MA arvutatakse reede sildiga nädalasulgemistest ning muutub kasutatavaks järgmisel esmaspäeval. Praeguse nädala lõpphinda varasematele päevadele ei kanta. Graafiku nädalaküünlad on ainult kuvamisviis; sündmused, ATR ja 5–60 päeva tulemused arvutatakse päevadel. Viimane nädalaküünal võib olla pooleli.

## Puutetsoon ja sündmused

EMA=100 ja tolerants=1% annab tsooni [99,101]. ATR-režiimis poollaius on ATR × kordaja. Kohandatud režiimis võetakse protsendilaiuse, ATR-laiuse ja dollaripõranda maksimum.

Puutepäev on sulgemine tsoonis või [Low,High] kattumine tsooniga. Sündmuse registreerimiseks peab olema teada eelnev tsooniväline sulgemispool. `min_touch` loendab järjestikuseid puutepäevi; sündmuse kuupäev on nõutava arvu saavutamise päev, mitte tagantjärele esimene puutepäev. Lähedased puuted liidetakse aktiivseks sündmuseks. Uus sündmus lubatakse, kui puutepäevade indeksite vahe ületab `gap` väärtuse.

Iga registreeritud puude avab kinnituse ooteoleku. Järgnev sama poole tsooniväline sulgemine tähendab põrget; vastaspoole sulgemine läbimurret. Kinnitus võib nõuda mitut järjestikust päeva ning minimaalset suunalist hinnamuutust registreerimishinnast. Aegunud kinnitus jäetakse kõrvale. Üks sündmus annab maksimaalselt ühe kinnitatud signaali. Üle kogu tsooni hüppav hinnalõhe võib anda läbimurde ilma puutepäevata. Uue eraldiseisva puute tekkimine asendab vana kinnitamata ooteoleku.

Puude ja läbimurre ei ole tingimata eraldiseisvad strateegiad; selles versioonis koondatakse nende suunatootlused. JSON-i `kind` võimaldab neid eraldi uurida.

## Tehingud ja tulemuslikkus

Signaal päeva i lõpus → sisenemine päeva i+1 avamisel. H-päevane tehing lõpeb päeva i+H sulgemisel. Pikk positsioon saab suuna +1, lühike −1.

`net_% = 100 × [suund × (väljumine/sisenemine − 1) − (2×fee_bps + spread_bps)/10000]`

See on aritmeetiline tootlus algse nominaali kohta, mitte võimendatud konto tootlus. Hinnavahe on kogu edasi-tagasi kulu, tasu rakendub mõlemale poolele. Laenukulud ja turumõju puuduvad.

MAE arvestab pika positsiooni väikseimat Low'd, lühikese suurimat High'd ning samu fikseeritud kulusid. Näidatakse kõige ebasoodsamat MAE-d üle hinnatud tehingute. Positiivsete tulemuste osakaal loeb ainult rangelt positiivse netotulemuse.

Iga MA, valimi ja horisondi sees valitakse esimene tehing ning järgmine alles pärast eelmist väljumist. Tabeli `n / eligible` tähendab kasutatud tehinguid / täieliku tulemusega signaale enne kattuvuse eemaldamist. Erinevate MA-de ja horisontide tehingud võivad kattuda: neid ei tohi käsitleda ühe portfellina.

Osta-ja-hoia võrdlus kasutab vastava valimi esimese päeva avamist ja viimast sulgemist koos kuludega. See on teise kestusega võrdlus; keskmine signaalitootlus ei tähenda paremat kogutootlust. Jagunemispiiri ületavaid tehinguid ega pooliku tulevikuhorisondiga viimaseid signaale statistikasse ei lisata.

## Otsinguskoor

Olgu N treeningu kauplemispäevade arv, T treeningus registreeritud puudete arv ja O sulgemiste tsoonis viibimise osakaal.

- `V = min(1, T / max(1,N/20)) × (1−O)`
- `Q = (0.5 + 0.5×tanh(keskmine_netotootlus/3)) × min(1,tehinguid/10)`
- Visuaalne skoor: `100×V`
- Signaaliskoor: `100×Q`
- Kombineeritud skoor: `100×[w×V+(1−w)×Q]`

Kaal w ja hindamishorisont on kasutaja määrata. Tolerants, kinnituse reeglid ja kulud on otsingu vältel fikseeritud. Automaatotsing optimeerib MA tüüpi ja perioodi, mitte kõiki parameetreid korraga. Kui tehinguid pole, on Q=0. Skoor on selgitatav heuristik, mitte statistiline tõenäosus ega tootlusprognoos. Pikkade puuduvate MA osadega kandidaadil peab treeningus olema vähemalt 20 arvutatud väärtust.

## Sõltumatu kontroll

Otsing saab ainult treeningandmed. Alles järjestuse fikseerimise järel arvutatakse TOP 5 testitulemused. Puuteseisundi ja keskmiste eelajalugu kantakse testiperioodi edasi, nagu päriselus; ettepoole hindu ei loeta.

Walk-forward kasutab kasvavat treeningakent (vaikimisi 504 päeva) ja eraldiseisvaid 126-päevaseid testiaknaid. Igas aknas valitakse MA uuesti ainult sellele eelnevalt ajaloost. Piiri ületavaid tehinguid ei hinnata. Tulemusi ei liideta automaatselt kapitalikõveraks.

Järelduse tugevust piiravad valimi suurus, ajas sõltuvus, kandidaatide paljusus, andmekvaliteet, ettevõtete valik ning hinnakorrigeerimised. Korrigeeritud ajaloolised hinnad võivad andmepakkujal hiljem muutuda; see pole ajalooliste andmeversioonide point-in-time arhiiv.
