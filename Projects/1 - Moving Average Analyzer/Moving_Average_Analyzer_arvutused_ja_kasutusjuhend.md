# Moving Average Analyzer: arvutuste, meetodite ja parameetrite kasutusjuhend

**Projekt 1/6 · USA aktsiate analüüs · investeerimishorisont 1–12 nädalat**  
**Versioon:** 1.0 · 4. november 2026  
**Alus:** projekti praegune `dist/engine.py`, `dist/app.js` ja metoodikadokument.

> **Eesmärk:** leida hinnagraafikult selgelt tõlgendatavaid kokkupuuteid libisevate keskmiste ümbrusega ning kontrollida, milline hinnaliikumine neile ajalooliselt järgnes. Parameetrite soovitused allpool on põhjendatud lähtepunktid uurimiseks, mitte empiiriliselt tõestatud parimad kauplemisparameetrid.

## 1. Projekti idee lühidalt

Hind ei pea keskmisega täpselt kokku langema. Keskmise ümber määratakse **puutetsoon**, mille sees hinnaliikumist käsitletakse ligikaudse puudutusena.

Näiteks EMA väärtusega 100 dollarit ja tolerantsiga 1% annab tsooni 99–101 dollarit. Hind 100,60 dollarit on selle reegli järgi keskmise lähedal, kuigi matemaatiliselt pole hind ja EMA võrdsed.

| Idee | Selgitus | Miks seda vaja on? |
|---|---|---|
| Ligikaudne puude | Kasutatakse tsooni, mitte täpset võrdsust | Väldib juhuslikust senditäpsusest sõltuvat analüüsi |
| Eraldiseisev sündmus | Lähedased puutepäevad liidetakse | Viis päeva ühe keskmise ümber pole tingimata viis uut võimalust |
| Kinnitatud signaal | Puutele peab järgnema määratud tingimusega sulgemine | Puude üksi ei näita edasist suunda |
| Automaatne ja manuaalne võrdlus | Algoritmi kandidaate saab muuta ja võrrelda | Kasutaja saab uurida, kas tulemus on arusaadav ja stabiilne |
| Treening ja test | Parameetrid leitakse varasemal ning hinnatakse hilisemal ajal | Eristab ajaloolist sobitamist uutest vaatlustest |
| Ühine Pythoni mootor | Sama arvutusloogika brauseris, Pythonis ja Colabis | Väldib eri keskkondades erinevate valemite kasutamist |

**Oluline eristus:** MA periood, analüüsiperiood ja signaali hindamishorisont on kolm eri asja. EMA 21 kasutab 21 päeva silumisparameetrit; 3-aastane analüüsiperiood määrab uuritava ajaloo; 20-päevane horisont määrab signaalijärgse tehingu kestuse.

## 2. Soovitatav esimene seadistus

Alusta päevagraafikust, kolmeaastasest ajaloost ja kolmest käsitsi määratud keskmisest: **EMA 21, SMA 55, EMA 100**. Need annavad kolm eri kiirusega võrdlusjoont. Numbrid pole maagilised: näiteks 20 ja 21 või 50 ja 55 vahel ei tohiks toimiva üldise mustri puhul olla dramaatilist vahet.

### 2.1. Üldseaded ja otsing

| Seade | Praegune vaikeväärtus | Soovitatav algväärtus | Põhjendus |
|---|---|---|---|
| Analüüsiperiood | 1 aasta | **3 aastat** | Rohkem võimalusi treeningu ja testi sündmuste kogumiseks; ei taga siiski piisavat valimit |
| Graafik / MA ühik | Päev / päevad | **Päev / päevad** | Sobib 5–60 kauplemispäeva tulemuste tõlgendamiseks |
| Käsitsi MA-d | EMA 21, SMA 55, EMA 100 | **Samad kolm** | Kiirem reaktsioon, keskmine trend ja aeglasem taust |
| Otsingu tüübid | SMA, EMA, WMA | **Kõik kolm** | Võimaldab võrrelda kaalumise mõju |
| Minimaalne periood | 5 | **10** | Esimeses katses vähendab väga lühikeste joonte osakaalu |
| Maksimaalne periood | 250 | **150** | Piisavalt lai esimene vahemik; pikemad perioodid saab lisada eraldi katsena |
| Otsingusamm | 1 | **5** | Kiirem ja lihtsam esimene võrdlus, vähem peenhäälestamist |
| Optimeerimise eesmärk | Kombineeritud | **Kombineeritud** | Arvestab nii visuaalset sobivust kui ka signaalide tulemust |
| Visuaalne kaal | 0,5 | **0,5** | Kumbki osa ei domineeri lähteülesandes |
| Otsingu hindamishorisont | 20 päeva | **20 päeva** | Ligikaudu neli kauplemisnädalat; lisaks vaata kõiki viit horisonti |
| Treeningu osa | 0,7 | **0,7 ehk 70%** | Jätab lõpuosa kontrolliks, säilitades suurema osa parameetrite otsingule |
| Joone paksus | 2 | **2** | Kolm joont jäävad hästi eristatavaks |
| Tsoonide kuvamine | Sees | **Sees** | Aitab mõista, miks algoritm puudutuse registreeris |

Vahemik 10–150 sammuga 5 annab **29 perioodi × 3 tüüpi = 87 kandidaati**. Vaikimisi 5–250 sammuga 1 annab **738 kandidaati**. Väiksem otsing vähendab arvutusaega ja katsetuste hulka, kuid ei kõrvalda üleoptimeerimise ohtu.

### 2.2. Puuted, kinnitus ja kulud

| Seade / JSON-võti | Vaikeväärtus | Soovitatav algväärtus | Põhjendus |
|---|---|---|---|
| Meetod `zone` | `percent` | **`percent`** | Protsenditsooni on kõige lihtsam graafikul kontrollida |
| Tolerants `tolerance` | 1% | **1%** | Arusaadav lähtepunkt; 100-dollarilise MA ümber ±1 dollar |
| ATR kordaja `atr_mult` | 0,5 | **0,5 ATR-režiimi katses** | Pool keskmisest päevasest true range'ist; ei mõju puhtas protsendirežiimis |
| Dollaripõrand `custom_floor` | 0,25 dollarit | **Esialgu mitte kasutada; kohandatud režiimis alusta 0-st** | Fikseeritud dollarilaius mõjutab odavat ja kallist aktsiat väga erinevalt |
| Puute alus `touch` | `range` | **`range` ehk High/Low** | Märkab ka päevasisest tsoonini jõudmist |
| Järjestikuseid päevi `min_touch` | 1 | **1** | Ühepäevane puudutus võib olla asjakohane; suunda kontrollib eraldi kinnitus |
| Puutevahe `gap` | 3 | **3** | Ühendab lähestikku toimuvad puuted; tundlikkuskatses võrdle väärtusega 5 |
| Lähenemise suund `side` | `both` | **`both`** | Esmane ülevaade sisaldab mõlema poole sündmusi |
| Kinnitus `confirm` | `zone` | **`zone`** | Lihtne reegel: hilisem sulgemine väljaspool tsooni |
| Liikumislävi `confirm_pct` | 1% | **1% ainult protsendikinnituse katses** | Tavalises tsoonikinnituses see parameeter tulemust ei muuda |
| Kinnituspäevi `confirm_bars` | 1 | **1; kontrollkatse 2** | Üks päev annab varasema signaali, kaks nõuavad püsivamat kinnitust |
| Kinnituse aegumine `timeout` | 15 päeva | **10 päeva** | Esmase katsena seob kinnituse kuni umbes kahe nädala taguse puudutusega |
| Tasu ühe poole kohta `fee_bps` | 5 bp | **5 bp katse-eeldus** | Lisa sisenemise ja väljumise kulu; asenda hiljem enda tingimustega |
| Edasi-tagasi hinnavahe `spread_bps` | 5 bp | **5 bp katse-eeldus** | Väldib kuludeta hinnangu kasutamist; pole turult mõõdetud spread |

**5 bp = 0,05%.** Algseadistuse edasi-tagasi kogukulu on `2 × 5 + 5 = 15 bp = 0,15%`.

Kuludele tee eraldi tundlikkuskatse, näiteks tasu 10 bp poole kohta ja spread 10 bp. See annab kogukuluks 0,30%. Need on analüüsi stsenaariumid, mitte väide ühegi maakleri tegelike tasude kohta.

## 3. Libisevate keskmiste arvutused

Olgu $C_t$ päeva sulgemishind ja $n$ periood.

### SMA — lihtne libisev keskmine

$$
SMA_t=\frac{1}{n}\sum_{j=0}^{n-1}C_{t-j}
$$

Kõik aknas olevad hinnad saavad sama kaalu. Hindade 98, 100 ja 102 korral on SMA 3 väärtus 100.

**Kasuta:** lihtsa ja läbipaistva trendivõrdlusena. Akna vanima hinna eemaldumine võib joont muuta isegi siis, kui uus hind pole ebatavaline.

### EMA — eksponentsiaalne libisev keskmine

$$
\alpha=\frac{2}{n+1},\qquad EMA_t=\alpha C_t+(1-\alpha)EMA_{t-1}
$$

Rakendus kasutab Pandase `ewm(span=n, adjust=False, min_periods=n)` meetodit. Algväärtus on esimene sulgemishind; enne n vaatlust tulemust ei näidata. EMA sisaldab kahaneva kaaluga ka vanema ajaloo mõju, mitte ainult viimast n hinda.

**Näide:** EMA 3 korral on $\alpha=0,5$. Hindade 98, 100, 102 rekursioon annab 98 → 99 → 100,5. Esimene kuvatav väärtus on 100,5.

**Kasuta:** kui soovid hiljutiste hinnamuutuste suhtes tundlikumat võrdlusjoont.

### WMA — kaalutud libisev keskmine

$$
WMA_t=\frac{nC_t+(n-1)C_{t-1}+\cdots+1C_{t-n+1}}{n(n+1)/2}
$$

Vanim hind saab kaalu 1 ja uusim n. Hindade 98, 100, 102 korral:

$$
WMA_3=\frac{1\cdot98+2\cdot100+3\cdot102}{6}\approx100,67
$$

**Kasuta:** EMA kõrval alternatiivse kiirema reaktsiooniga keskmisena. Sama n ei tähenda SMA, EMA ja WMA puhul sama efektiivset viivitust.

## 4. Puutetsooni valimine

### Protsenditsoon

Kui MA väärtus on $M_t$ ja tolerants $p$ protsenti:

$$
w_t=M_t\frac{p}{100},\qquad L_t=M_t-w_t,\qquad U_t=M_t+w_t
$$

MA=100 ja p=1 annab [99,101]. Tolerants 1,4 annab [98,6;101,4]. **1% tähendab poollaiust**: tsooni kogulaius on 2% MA väärtusest.

**Sobib:** esimeseks visuaalseks uurimiseks ja lihtsaks tõlgendamiseks. Võrdle eelnevalt kokku lepitud väärtusi 0,7%, 1% ja 1,4%; ära vali ainult kõige ilusama testi järgi.

### ATR-põhine tsoon

$$
TR_t=\max(H_t-Low_t,\ |H_t-C_{t-1}|,\ |Low_t-C_{t-1}|)
$$

$$
ATR_{14,t}=\frac{1}{14}\sum_{j=0}^{13}TR_{t-j},\qquad w_t=k\,ATR_{14,t}
$$

Siin tähistab $Low_t$ päeva madalaimat hinda; $L_t$ eelmises alajaotuses oli tsooni alumine piir.

Rakenduse ATR on **14 päeva lihtne keskmine**, mitte Wilderi silutud ATR. Periood 14 on koodis fikseeritud, veebiliideses muudetakse kordajat.

**Näide:** MA=100, ATR=4 ja k=0,5 annavad [98,102]. Rahulikuma turu ATR=1 korral on tsoon [99,5;100,5].

**Sobib:** katseks, kus soovid tsooni laiuse kohandumist hinnakõikumistega. ATR ei taga õiget tsoonilaiust; liiga suur kordaja võib muuta puute tavaliseks hinnamüraks.

### Kohandatud tsoon

$$
w_t=\max\left(M_t\frac{p}{100},\ kATR_{14,t},\ f\right)
$$

$f$ on minimaalne poollaius dollarites. Meetod võtab **suurima**, mitte keskmise kolmest komponendist.

**Näide:** protsendilaius 1 dollar, ATR-laius 1,5 dollarit ja põrand 0,25 dollarit → poollaius 1,5 dollarit.

Kasuta alles siis, kui oskad põhjendada iga komponendi rolli. 0,25-dollariline põrand on 5-dollarilise aktsia puhul juba 5%, kuid 500-dollarilise puhul ainult 0,05%.

## 5. Kuidas puudest saab sündmus ja signaal?

### 5.1. Puutumise tingimus

| Valik | Tingimus | Tõlgendus |
|---|---|---|
| Sulgemishind | $L_t\le C_t\le U_t$ | Päev lõppes tsoonis |
| High/Low | $Low_t\le U_t$ ja $H_t\ge L_t$ | Päeva hinnavahemik kattus tsooniga |

High/Low kontroll kasutab päeva lõpus teada olevat MA-d. See ei rekonstrueeri päevasisest hinnateekonda ega tõesta, et päeva sees oli samasugune MA. Seetõttu on tegemist päeva lõpu analüüsiga.

### 5.2. Puudete liitmine

- `min_touch=1`: üks puutepäev võib sündmuse avada.
- `min_touch=2`: vaja on vähemalt kahte järjestikust puutepäeva. Sündmus registreeritakse teisel päeval, mitte tagantjärele esimesel.
- `gap=3`: uus sündmus lubatakse siis, kui praeguse ja viimase puutepäeva **reaindeksite vahe on suurem kui 3**.

Näiteks kui viimane puude oli indeksil 10, ei ava puudutus indeksil 13 veel uut sündmust; indeksil 14 võib avada. Puuduvad kauplemispäevad CSV-s muudavad reaindeksite tähendust, seega kasuta täielikku päevast hinnaseeriat.

Puuteseeria lähenemispool määratakse varasema tsoonivälise sulgemise järgi. Kui sellist varasemat poolt pole teada, ei registreerita sellest veel suunaga puutesündmust.

**Suund „ülevalt” ei tähenda „ainult ostusignaalid”.** Ülevalt lähenemisele võib järgneda põrge üles või läbimurre alla.

### 5.3. Neli signaalitüüpi

| Lähenemispool | Hilisem kinnitatud sulgemine | Signaal |
|---|---|---|
| Ülevalt | Üle tsooni ülemise piiri | Põrge üles |
| Ülevalt | Alla tsooni alumise piiri | Läbimurre alla |
| Alt | Alla tsooni alumise piiri | Põrge alla |
| Alt | Üle tsooni ülemise piiri | Läbimurre üles |

Tavaline puutejärgne kinnitus tekib kõige varem **järgmisel päeval pärast sündmuse registreerimist**. Üle kogu tsooni hüppav hinnalõhe võib tekitada läbimurde ka ilma puutepäevata; ühe kinnituspäeva korral võib signaal tekkida hüppepäeva sulgemisel.

Protsendikinnituses peab hind lisaks tsoonist väljumisele liikuma registreerimise sulgemishinnast vajalikus suunas vähemalt `confirm_pct` protsenti. Mitme kinnituspäeva korral peab tingimus kehtima järjest ning suund säilima. Võrdlus toimub iga päeva jooksva tsooniga, mitte puutepäeva külmutatud tsooniga.

Üks puutesündmus annab kuni ühe kinnitatud signaali. Uus eraldiseisev puude võib asendada vana kinnitamata ooteoleku. Aegunud sündmusest signaali ei teki. `gap` liidab puuteid; see pole kõikidele hinnalõhe-läbimurretele universaalne signaalide vahepiirang.

## 6. Automaatse optimeerimise kolm eesmärki

Otsing proovib lubatud MA tüüpe ja perioode. **Tolerants, kulud, kinnitusreeglid ja hindamishorisont jäävad ühe otsingu jooksul fikseerituks.** Nende automaatset ühisoptimeerimist praeguses versioonis pole.

### A. Visuaalne sobivus

Eesmärk on piisav arv eraldiseisvaid puudutusi ilma selleta, et hind veedaks peaaegu kogu aja tsoonis.

Olgu N treeningu päevade arv, T puutesündmuste arv ning O tsoonis olevate sulgemiste osakaal:

$$
V=\min\left(1,\frac{T}{\max(1,N/20)}\right)(1-O)
$$

Skoor on $100V$. Puutearvu mõju küllastub ligikaudu ühe puute juures iga 20 treeningpäeva kohta. See 20 on **skoori fikseeritud konstant**, mitte kasutaja valitud tootluse hindamishorisont.

Skoor ei mõõda graafiku ilu otseselt. See on lihtne arvuline lähendus: eraldi sündmused ja tsoonis viibimine.

### B. Signaalide tulemuslikkus

Olgu $\bar r$ keskmine kuludejärgne suunatootlus **protsendipunktides** ja n mittekattuvate hinnatud tehingute arv:

$$
Q=\left(0,5+0,5\tanh(\bar r/3)\right)\min(1,n/10)
$$

Skoor on $100Q$. Konstant 3 määrab tootluse skaleerimise ja 10 valimimahu teguri küllastumise. **Kümme tehingut ei tõenda statistilist usaldusväärsust.** Null tehingut annab Q=0.

### C. Kombineeritud tulemus

$$
S=100\left(wV+(1-w)Q\right)
$$

- w=0,5: mõlemale osale võrdne kaal.
- w=0,7: rohkem rõhku visuaalsele puutestruktuurile.
- w=0,3: rohkem rõhku signaalide ajaloolisele tulemusele.

**Arvuline näide:** N=200, T=12 ja O=0,2 annavad V=0,8. Kui tehinguid on 8 ja keskmine netotootlus 1,5%, siis Q≈0,585. Kaaluga 0,5 on koguskoor ligikaudu **69,2**. See ei ole 69,2% edutõenäosus ega tootlus.

TOP 5 järjestus põhineb treeningul. Testitulemused arvutatakse pärast kandidaatide järjestamist. Kui valid nende seast kõrgeima testitootlusega kandidaadi, oled kasutanud testi parameetri valimiseks.

## 7. Signaalijärgse tulemuse arvutamine

Signaal päeva i lõpus → sisenemine päeva i+1 avamisel → väljumine päeva i+H sulgemisel.

| H | Ligikaudne kestus |
|---|---|
| 5 kauplemispäeva | 1 nädal |
| 10 | 2 nädalat |
| 20 | 4 nädalat |
| 40 | 8 nädalat |
| 60 | 12 nädalat |

Börsipühad muudavad kalendrikestust. Kui kõiki H tulevikupäevi pole, tehingu tulemust statistikasse ei lisata. Signaal võib sellegipoolest graafikul nähtav olla.

### Netotootlus

$$
r_{net}=100\left[d\left(\frac{P_{exit}}{P_{entry}}-1\right)-\frac{2f+s}{10000}\right]
$$

$d=+1$ üles- ja $d=-1$ allasuunalise signaali korral; f on tasu ühe poole kohta ning s edasi-tagasi spread baaspunktides.

**Näide:** sisenemine 100, väljumine 104, suund +1, f=5, s=5 → 4%−0,15%=**3,85%**. Allasuunalise signaali korral annab sama hinnatõus −4%−0,15%=**−4,15%**.

Langussignaali tootlust käsitletakse siin hüpoteetilise lühikese positsioonina algse nominaali suhtes. See ei arvesta aktsialaenu kättesaadavust ega laenukulu. Rakendus ei saada tehingukorraldusi.

### Statistika lugemine

| Näitaja | Mida see tähendab? | Mida sellest ei järeldu? |
|---|---|---|
| Tehinguid `n / eligible` | Kasutatud tehingud / täieliku horisondiga signaalid enne kattuvuse eemaldamist | Kõik nähtavad signaalid ei kuulu valimisse |
| Keskmine | Netotootluste aritmeetiline keskmine | Ei ole portfelli kogutootlus |
| Mediaan | Järjestatud tulemuste keskmine väärtus või kahe keskse keskmine | Ei kirjelda üksinda äärmusriski |
| Positiivsete osakaal | Rangelt positiivse netotulemusega tehingute osa | Kõrge osakaal ei taga kasumit, kui kaotused on suured |
| Halvim MAE | Kõige ebasoodsam tehinguaegne hinnaliikumine hinnatud tehingute hulgas, koos kuludega | Ei ole portfelli maksimaalne langus ega stop-loss |
| Osta ja hoia | Kogu vastava treeningu/testi alguse avamisest lõpu sulgemiseni saadud tootlus | Pole sama kestusega kui keskmine signaalitehing |

Pika tehingu MAE kasutab tehingu madalaimat Low'd, lühikese kõrgeimat High'd. Näiteks pika positsiooni sisenemine 100 ja madalaim hind 96 annavad algkuludega MAE=**−4,15%**, ka siis, kui tehing lõpeb kasumis.

Positiivsete osakaalu kohal hiirt hoides näeb Wilsoni 95% vahemikku. See väljendab väikese valimi ebakindlust, kuid ei arvesta täielikult aegridade sõltuvust ega paljude kandidaatide läbiproovimist.

Kattuvus eemaldatakse **iga MA, horisondi ja valimi sees eraldi**: järgmine tehing saab siseneda alles pärast eelmise väljumispäeva. See vähendab samade hinnaliikumiste korduvat arvestamist, kuid ei muuda tehinguid automaatselt statistiliselt sõltumatuks.

## 8. Treening, test ja walk-forward

### Ühekordne jaotus

70% varasematest valitud perioodi ridadest kasutatakse treeninguks ja 30% hilisematest testiks. Andmeid ei segata juhuslikult. Graafikule eelnevat ajalugu kasutatakse MA soojenduseks.

Treeningu tehing peab ka lõppema treeningus. Jagunemispiiri ületav tulemus jäetakse välja. Testi signaalid võivad kasutada varasemat MA- ja puuteseisundit, sest see info oli testipäevaks olemas.

**Praktiline tööreegel:** määra eesmärk ja parameetrite võrdlusplaan enne testitulemuste vaatamist. Kui testi järgi edasi muudad, käsitle seda perioodi arendusandmetena ning jäta lõplikuks kontrolliks uus puutumatu ajavahemik.

Rakendus hoiatab alla 10 testtehingu korral. Kui valim on vähemalt 10 ning treeningu keskmine on positiivne, kuid testi oma mitte, kuvab rakendus võimaliku üleoptimeerimise hoiatuse. Väikese valimi hoiatus on praeguses liideses esikohal; see ei tähenda, et treeningu ja testi vastuolu puuduks.

### Walk-forward

Pythoni skriptis `scripts/walk_forward.py` kasutatakse vaikimisi:

- esmane treening: **504 kauplemispäeva**, ligikaudu kaks aastat;
- üks testiosa: **126 kauplemispäeva**, ligikaudu pool aastat;
- treening kasvab pärast iga testiosa;
- järgmise testiosa MA valitakse ainult sellele eelneva ajaloo järgi.

Näiteks 1008 päeva annab 504-päevase algtreeningu järel neli 126-päevast testi. Käsurea skripti otsing on 5–100 sammuga 5; Colabi näide kasutab väiksemat 10–60 vahemikku sammuga 10.

Walk-forward on praegu **Pythoni/Colabi funktsioon**, veebilehel eraldi nuppu pole. Tulemused tagastatakse akende kaupa; need ei moodusta automaatselt kapitalikõverat.

## 9. Nädalagraafiku eripära

Nädalagraafikule lülitumisel muutub MA perioodi ühik: **EMA 21 tähendab 21 nädalat**, mitte 21 päeva. Esimeseks nädalaseks võrdluseks sobivad uurimise lähtepunktina näiteks EMA 4, SMA 11 ja EMA 20, kuid need pole päevase EMA 21 / SMA 55 / EMA 100 täpsed ekvivalendid.

Nädala MA kasutab lõppenud nädala viimast sulgemist ja muutub rakenduses kättesaadavaks järgmisel esmaspäeval. Poolelioleva nädala tulevast sulgemist ei kanta varasematele päevadele.

**Puuted, kinnitused, ATR, puutevahe ja 5–60 päeva tootlused jäävad päevapõhiseks.** Seetõttu võivad signaalid asuda nädalaküünalde vahel. Viimane nädalaküünal võib olla pooleli. Pikkade nädalaperioodide jaoks on vaja piisavalt pikka eelajalugu.

## 10. Soovitatav tööjärjekord veebilehel

1. **Laadi aktsia.** Kontrolli sümbolit, andmeallikat ja viimast hinnapäeva.
2. **Vali 3 aastat ja päevagraafik.** Jäta esmalt EMA 21, SMA 55 ja EMA 100.
3. **Määra 1% tsoon ja High/Low puude.** Hoia tsoonipiirid nähtaval.
4. **Määra kinnitus ja kulud enne otsingut.** Näiteks 1 kinnituspäev, 10-päevane aegumine, 5/5 bp kulueeldused.
5. **Käivita kombineeritud otsing 10–150, samm 5.** Vaata esmalt treeningu puutestruktuuri ja sündmuste arvu.
6. **Lisa kandidaadid graafikule.** „Taasta automaatne tulemus” taastab viimase otsingu seaded ja kaks parimat MA-d. Statistika rippmenüüst saad nende tulemusi vahetada.
7. **Kontrolli mõõdukat parameetrimuutust treeningus.** Näiteks periood 35 → 40 või tolerants 1% → 1,4%. Stabiilsus naaberparameetritel on kasulikum tähelepanek kui üks erandlik maksimum.
8. **Vaata eraldi testiosa.** Hinda tehingute arvu, keskmist, mediaani, MAE-d ja kulutundlikkust. Ära võrdle ainult võiduprotsenti.
9. **Salvesta seadistus ja ekspordi tulemused.** Märgi üles katse eesmärk ja muudatused.
10. **Korda fikseeritud reeglitega teisel perioodil või walk-forward-kontrollis.** Ära esita korduvat testile kohandamist sõltumatu tõendina.

„Võrdle konfiguratsioone” arvutab praegused MA-d ümber sama ühise tolerantsi ja signaalireeglistikuga. Kahe eri tolerantsi või kulumudeli võrdlemiseks salvesta eraldi JSON-seadistused ja tulemused ning vaheta nende vahel; praegune leht ei kuva kahte terviklikku parameetripaketti kõrvuti.

Seadistuse JSON sisaldab parameetreid ja jooni, mitte imporditud hinnafaili. Teises brauseris tuleb oma CSV vajadusel uuesti importida. TOP 5 on viimase otsingu tulemus: pärast parameetrimuudatust käivita uus otsing, kui tahad uut järjestust. Tulemuste eksport säilitab jooksva analüüsi; otsingu `ranking` on jooksvas tulemuses olemas vahetult pärast optimeerimist, hilisem käsitsianalüüs seda loendit ei säilita. Täieliku otsingujälje jaoks ekspordi kohe pärast otsingut.

## 11. Probleemide tõlgendamine

| Tähelepanek | Võimalik põhjus | Järgmine kontroll |
|---|---|---|
| Graafik on tähiseid täis | Tsoon liiga lai või sündmuste vahe liiga väike | Kitsenda tsooni või võrdle `gap=5` |
| Laiem tsoon annab vähem sündmusi | Varem eraldi puuted liitusid üheks | Vaata puuteseeriaid, mitte ainult koguarvu |
| Signaale on vähe | Pikk MA, kitsas tsoon või range kinnitus | Kontrolli eelajalugu ja reegleid enne perioodi muutmist |
| 60 päeva tabelis on null tehingut | Lühike test või liiga hilised signaalid | Pikenda analüüsiperioodi; ära täida puuduvat tulevikku oletustega |
| Treening hea, test halb | Juhuslik sobitus, režiimimuutus või väike valim | Kontrolli naaberparameetreid ja uusi ajavahemikke |
| Võiduprotsent kõrge, keskmine negatiivne | Vähesed suured kaotused | Vaata mediaani, üksiktehinguid ja MAE-d |
| MA puudub graafiku alguses | Soojenduseks pole piisavalt hindu | Impordi pikem ajalugu või lühenda MA perioodi |
| Nädalavaates tulemus muutus palju | Perioodi ühik muutus päevast nädalaks | Kohanda MA perioodid teadlikult |
| Võõras sümbol ei laadi | Selle JSON-faili pole staatilises andmepaketis | Impordi CSV/JSON või kasuta projekti andmelaadimise skripti |

## 12. Edasiarenduse ideed

Järgnevad ideed on **järgmised võimalikud arendused**, mitte praeguse versiooni olemasolevad omadused.

| Idee | Lühikirjeldus | Mida see selgitaks või parandaks? |
|---|---|---|
| Parameetrite stabiilsuskaart | Periood × tolerants soojuskaart treeningandmetel | Kas hea tulemus on lai piirkond või üks juhuslik tipp? |
| Signaalitüüpide eraldi tabel | Põrked ja läbimurded ning üles/alla suunad eraldi | Praegune koondtulemus võib varjata ühe alamtüübi nõrkust |
| Võrdne mõõdupuu ostu-ja-hoiaga | Samade ajavahemike võrdlus ja kapitalikõver | Võimaldaks rääkida strateegia kogutootlusest, mitte ainult keskmisest sündmusest |
| Puhas lõppkontroll | Eraldi valideerimis- ja lõplik testiosa | Vähendaks testi korduva kasutamise mõju |
| Walk-forward veebiliideses | Olemasoleva Pythoni meetodi juhtpaneel | Muudaks ajas korduva kontrolli lihtsamaks |
| Turuolukorra jaotus | Tõusva, langeva ja külgsuunalise perioodi analüüs | Näitaks, millistes oludes muster esineb |
| Ühine andmekiht kuuele moodulile | Sama sümbol, kuupäevad, andmeallikas ja versioon | Lubaks hiljem siduda hinna, optsioonid, uudised ja fundamentaalnäitajad |
| AI selgitaja | LLM koostab arvutatud tulemustest kontrollitava selgituse | Aitaks tõlgendada raporteid; arvutused ja signaalid jääksid Pythoni ülesandeks |

## 13. Reprodutseeritava katse meelespea

- Salvesta sümbol, hinnainfo kuupäev ja andmete korrigeerimise viis.
- Salvesta kogu parameetrikomplekt, mitte ainult MA periood.
- Pane kirja, mitu seadistust oled proovinud ja millal vaatasid testi.
- Ära tõlgenda skoori tõenäosusena ega keskmist tehingut portfelli tootlusena.
- Ära nimeta mittekattuvaid tehinguid tingimusteta sõltumatuteks vaatlusteks.
- Võrdle kulude ja lähestikuste parameetrite mõju.
- Erista kirjeldust „ajaloos sobis” väitest „tulevikus töötab”.

## Allikad ja teostuse piirid

Projekti arvutusreeglite peamine allikas on praegune lähtekood `dist/engine.py`; kasutajaliidese käitumise allikas on `dist/app.js`. Selle juhendi soovituslikud algväärtused on metoodilised valikud, mitte dokumentatsiooniallikatest tuletatud optimaalsed kauplemisparameetrid.

- [Pandas: eksponentsiaalse kaalumise meetodid](https://pandas.pydata.org/pandas-docs/version/2.2/user_guide/window.html) — EMA rekursiooni tehniline taust.
- [scikit-learn: TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) — ajaliselt järjestatud valideerimise põhimõte. Projekt kasutab enda walk-forward-teostust, mitte seda klassi.

Rakendus on sündmusuuring. Puuduvad positsioonide suuruse valik, stop-loss, kapitalijaotus, maksud, intress, lühikeseks müügi laenukulu ja turumõju. Korrigeeritud ajaloolised hinnad võivad hiljem muutuda; tegu pole ajalooliste andmeversioonide arhiiviga. Juhend dokumenteerib olemasolevat rakendust ega muuda selle lähtekoodi või vaikeväärtusi.
