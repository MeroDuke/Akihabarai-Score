# Windows digitális aláírás megvalósíthatósági vizsgálata

- Plan ID: `PLAN-012`
- Status: `proposed`
- Target release: `TBD`
- Type: `reliability`
- Priority: `medium`
- Created: `2026-09-29`
- Last reviewed: `2026-10-19`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A GitHub Actionsből letöltött Windows portable buildet a böngésző veszélyes
letöltésként blokkolhatja, mert a csomag aláíratlan futtatható állományt
tartalmaz. Ez a zárt béta alatt is közvetlen felhasználói súrlódást okozott.

A Windows Authenticode aláírás igazolhatja a kiadó személyazonosságát és a
bináris sértetlenségét, de a Microsoft SmartScreen reputáció ettől részben
külön mechanizmus. Ezért aláírás vásárlása vagy bevezetése előtt bizonyítani
kell, hogy a várható felhasználói előny arányban áll a költséggel és az
üzemeltetési kockázattal.

## Cél

- Feltárni a hobby/open-source projekt számára reális Windows code-signing
  lehetőségeket és teljes költségüket.
- Elkülöníteni az Authenticode aláírás, a tanúsítványba vetett bizalom, a
  SmartScreen reputáció és a böngészős letöltésvédelem hatását.
- Megtervezni a privát kulcs biztonságos CI-kezelését, időbélyegzését,
  rotációját és visszavonását.
- Bizonyíték alapján dönteni a bevezetésről vagy tudatos elvetésről.

## Ütemezési és döntési keret

A vizsgálat később, egy külön kiválasztandó release kísérő elemeként kerül
elő; önálló aláírás-vizsgálati release nem készül. Az adott kiadásnak az
aláírástól független feature- vagy QoL-tartalma is kell legyen. A célverzió
egyelőre `TBD`; annak kijelölése külön tulajdonosi döntés.

Akkor újra ellenőrizzük az aktuális szolgáltatásokat, árakat, jogosultságot és
felhasználói hasznot. A vizsgálat eredménye lehet bevezetés, halasztás vagy
elvetés; az aláírás elmaradása önmagában nem akadályozza a kiadás lezárását,
ha a döntés dokumentált. Vásárlás és tényleges integráció külön jóváhagyást
igényel, nem következik automatikusan a vizsgálat betervezéséből.

## Nem cél

- Tanúsítvány vagy szolgáltatás automatikus megvásárlása.
- Titkos kulcs repositoryba vagy általános CI artifactba helyezése.
- Annak ígérete, hogy az aláírás azonnal megszüntet minden SmartScreen- vagy
  böngészőfigyelmeztetést.
- Linux csomagok Windows Authenticode-dal történő kezelése.

## Jelenlegi állapot

A Windows `onefile` EXE és a portable ZIP nincs digitálisan aláírva. A CI a
buildet, natív inventoryt, startupot, crash diagnosztikát és portable layoutot
ellenőrzi, de kiadói aláírást nem készít. A GitHub Release és Actions artifact
hash-alapú sértetlenséget biztosíthat, kiadói OS-szintű bizalmat azonban nem.

## Előzetes kutatási jegyzet — 2026-10-19

Az alábbiak a tervezési beszélgetés során ellenőrzött szolgáltatói és platform-
dokumentációk összefoglalói, nem végleges beszerzési vagy kompatibilitási
bizonyítékok. Nem történt jelentkezés, ajánlatkérés, vásárlás vagy aláírt buildes
próba. A vizsgálat újranyitásakor minden változó feltételt újra validálni kell.

### Mit ad és mit nem garantál az aláírás?

- Az Authenticode a kiadói identitást és az aláírt fájl sértetlenségét igazolja;
  nem igazolja a program hibamentességét vagy ártalmatlanságát.
- A SmartScreen reputáció külön tényező. Érvényes aláírással is lehet
  figyelmeztetés; az EV-tanúsítvány sem jelent automatikus reputációs kivételt.
- Önaláírt tanúsítvány nem helyettesíti a publikus terjesztéshez szükséges
  megbízható kiadói láncot. Belső teszteléshez vagy kezelt gépeken más a szerepe.
- Az időbélyegzés és a lejárat/visszavonás ellenőrzése külön feladat; a
  tanúsítvány egyszerű lejárata nem azonos egy hibás aláírással.

Források:
[Microsoft aláírási lehetőségek](https://learn.microsoft.com/windows/apps/package-and-deploy/code-signing-options),
[SmartScreen reputáció](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation).

### Lehetséges beszerzési utak

| Út | Előzetes megállapítás | Újravalidálandó |
| --- | --- | --- |
| Microsoft Azure Artifact Signing | A publikus bizalmi modellben magánszemélyeknél USA/Kanada a támogatott kör; magyar magánszemélyként ez jelenleg nem járható. EU-s szervezetekre eltérő feltételek vonatkoznak. | Földrajzi jogosultság, identitásforma, teljes díj és CI-hozzáférés. |
| SignPath Foundation | Elfogadott open-source projekteknek ingyenes szolgáltatás; a tanúsítvány a Foundation nevére szól. Projekt- és reputációellenőrzés, ellenőrizhető build-eredet és aláírási szabályok szükségesek; elfogadás nem garantált. | Score és csomagolt függőségek jogosultsága, szerepkörök/review és jóváhagyás egy kis csapatnál, CI-integráció. |
| Certum Open Source | Magánszemélyes OSS-konstrukció identitásellenőrzéssel. A felhős változat webshopos induló ára a kutatáskor 49 EUR volt; a termékoldalon más konstrukcióhoz 25 EUR-tól ár is szerepelt, ezért ezek nem kezelhetők azonos teljes költségként. | Végleges időtartam, adók, csomagtartalom, kulcstárolás, aláírási kvóta és CI-automatizálhatóság. Saját kereskedelmi korlátozásaik külön vizsgálandók, nem vezethetők le pusztán a GPL-ből. |
| Normál saját tanúsítvány | Certum Standard magánszemélynek is elérhető; SSL.com külön IV konstrukciót és felhős aláírást kínál. Ez nem kizárólag OSS-projektek támogatási programja. | Magyarországi igénylés tényleges elfogadása, identitás és kiadói név, teljes költség, token/felhő, automatizálás és kvóták. |

Források:
[Microsoft jogosultság](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart),
[SignPath Foundation](https://signpath.org/),
[SignPath feltételek](https://signpath.org/terms.html),
[Certum konstrukciók](https://www.certum.eu/en/code-signing-certificates/),
[Certum webshop](https://shop.certum.eu/buy-a-code-signing-certyficate),
[Certum identitás- és OSS-feltételek](https://support.certum.eu/en/code-signing-required-documents/),
[SSL.com konstrukciók](https://www.ssl.com/products/software-integrity/code-signing/).

### Aldrod, Steam és közös kiadói infrastruktúra

Egy saját, általános code-signing tanúsítvány kiadói személyhez vagy szervezethez
kötődik, nem feltétlenül egyetlen terméknévhez. Ez alapján lehetséges vizsgálati
irány ugyanazt az infrastruktúrát az Aldrodhoz és a Score-hoz használni, ha
mindkettőnél ugyanaz a jogosult kiadó és a szerződés ezt megengedi. A konkrét
többprojektes felhasználás szolgáltatói megerősítést igényel; nem garantáljuk
a díj, kvóta vagy reputáció automatikus megoszthatóságát.

Külső játékkiadó tanúsítványa nem válik a fejlesztő szabadon felhasználható
tanúsítványává. Projektspecifikus OSS-támogatás sem vihető át automatikusan
egy másik vagy zárt forrású projektre.

A Valve nyilvános review-leírásában a kutatáskor nem találtunk általános
Windows Authenticode-követelményt. Ez nem a követelmény hiányának teljes körű
igazolása: az Aldrod kiadásakor a tényleges Steamworks-feltételeket külön
ellenőrizni kell. Steam-kiadásból, Steam DRM-ből vagy Steam Direct díjból nem
következik saját, más projekthez használható tanúsítvány megszerzése.

Források:
[Steam review](https://partner.steamgames.com/doc/store/review_process),
[Steam DRM](https://partner.steamgames.com/doc/features/drm),
[kiadói aláírási konstrukciók](https://www.ssl.com/products/software-integrity/code-signing/),
[SignPath projektszabályok](https://signpath.org/terms.html).

### Újravalidálási lista a célrelease kiválasztásakor

- Jogosult személy/szervezet és a tanúsítványban megjelenő nyilvános név.
- Aktuális szolgáltatói feltételek, országok, OSS- és kereskedelmi korlátozások.
- Teljes éves költség: adók, hardver vagy felhős kulcskezelés, kvóták, megújítás.
- Score és Aldrod közös használatának szerződéses és technikai lehetősége.
- CI-hitelesítés, kulcsvédelem, jóváhagyás, időbélyegzés, megújítás és visszavonás.
- Tényleges Windows letöltési/indítási próba a választott terjesztési csatornán.
- Döntés a bevezetésről, halasztásról vagy elvetésről, külön vásárlási engedéllyel.

## Vizsgálandó megoldások

- Hagyományos OV/EV code-signing tanúsítvány és annak hardveres vagy felhős
  kulcstárolási követelményei.
- Menedzselt felhős aláírási szolgáltatás CI-integrációval.
- Hobby- vagy open-source projekteknek elérhető támogatott programok.
- Több saját projekt közös kiadói aláírási infrastruktúrája, például egy
  későbbi Aldrod-kiadással együtt. Külön ellenőrizendő a tanúsítvány jogosultja,
  a szolgáltatói szerződés, kvóta, CI-hozzáférés és az OSS-programok
  projektspecifikus korlátozása. Steam-kiadásból nem feltételezünk automatikusan
  más projektekhez felhasználható tanúsítványt.
- Authenticode aláírás és megbízható időbélyegzés az EXE-n; szükség esetén a
  terjesztési csomag külön ellenőrző hashével.
- A jelenlegi GitHub Actions jogosultságok, fork/PR biztonság és release-only
  secret-hozzáférés.
- Aláírt és aláíratlan kontrollbuild valódi Windows/Edge/SmartScreen próbája.

## Platform- és kompatibilitási szempontok

Az elsődleges cél a Windows portable EXE. Linuxon külön csomagaláírási vagy
checksum-megoldás vizsgálható, de az nem része ennek a döntésnek. Az aláírásnak
a PyInstaller build és a natív audit után, de a ZIP elkészítése előtt kellene
történnie.

## Tesztstratégia

Az alábbi aláírt buildes tesztek csak külön jóváhagyott próba vagy bevezetés
esetén szükségesek. Halasztás vagy elvetés esetén a bizonyítékokkal alátámasztott
döntési rekord zárja le a vizsgálatot; nem kell ezért tanúsítványt vásárolni.

- Aláírás jelenlétének és láncának gépi ellenőrzése a CI-ben.
- Időbélyeg és bináris hash változásának ellenőrzése.
- Negatív teszt: hiányzó, sérült, visszavont vagy a választott bizalmi szabályok
  szerint érvénytelen aláírásnál a release job álljon meg. Érvényes időbélyeggel
  ellátott, azóta lejárt tanúsítványt ne utasítsunk el pusztán a lejárat miatt.
- Csomagolt startup, crash és portable regresszió az aláírt EXE-n.
- Manuális letöltési és SmartScreen-próba tiszta vagy alacsony reputációjú
  Windows környezetben.

## Elfogadási feltételek a vizsgálathoz

- [ ] Az aktuális szolgáltatók, jogosultsági feltételek és teljes éves költség
      összehasonlítása elkészült.
- [ ] Dokumentált, mit old meg az aláírás és mit nem garantál a SmartScreen
      szempontjából.
- [ ] A kulcskezelési és CI threat model elkészült.
- [ ] Van mérhető manuális próba vagy hiteles szolgáltatói bizonyíték a
      felhasználói haszonról.
- [ ] Tulajdonosi döntés született: bevezetés, halasztás vagy elvetés.
- [ ] A kiválasztott release az aláírástól független feature- vagy QoL-tartalommal
      rendelkezik; az aláírási döntés nem helyettesíti azt.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

A tanúsítvány és felhős kulcstárolás visszatérő költséget, identitás-ellenőrzést
és secret-management felelősséget jelenthet. Kompromittált kulcs esetén
visszavonás és újraaláírás szükséges. Ha a haszon nem igazolható, a jelenlegi
aláíratlan build és dokumentált hash marad a visszaállási pont.

## Nyitott kérdések

- Magánszemélyként vagy projekt/szervezet néven történne az identitás-ellenőrzés?
- Van-e elfogadható árú vagy támogatott hobby/open-source program a döntés
  időpontjában?
- A tényleges terjesztési csatornán mennyit javít az aláírás a letöltési és
  indítási élményen?
- Milyen release-gyakoriság mellett éri meg a visszatérő költség?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | Először csak megvalósíthatósági vizsgálat készül. | A felhasználói súrlódás valós, de a költség és a SmartScreen-hatás még nem ismert. |
| 2026-10-19 | Későbbi release kísérő vizsgálata, célverzió még nincs. | Ugyanabban a kiadásban önálló feature vagy QoL is készül; az aláírás elvetése is elfogadható eredmény. |
| 2026-10-19 | A több saját projekthez használható közös kiadói megoldást is vizsgáljuk. | Egy későbbi Aldrod-aláírás költsége és infrastruktúrája esetleg megosztható, de a jogosultság és a szolgáltatói feltételek újraellenőrzendők. |
| 2026-10-19 | A kezdeti kutatás forrásai és korlátai megőrzésre kerültek. | Később nem nulláról indulunk, de az árak, jogosultságok és platformfeltételek újravalidálása kötelező. |

## Megvalósítási napló
Még nem indult el.
