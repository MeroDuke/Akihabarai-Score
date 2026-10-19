# Windows digitális aláírás megvalósíthatósági vizsgálata

- Plan ID: `PLAN-012`
- Status: `proposed`
- Target release: `TBD`
- Type: `reliability`
- Priority: `medium`
- Created: `2026-09-29`
- Last reviewed: `2026-09-29`
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

## Vizsgálandó megoldások

- Hagyományos OV/EV code-signing tanúsítvány és annak hardveres vagy felhős
  kulcstárolási követelményei.
- Menedzselt felhős aláírási szolgáltatás CI-integrációval.
- Hobby- vagy open-source projekteknek elérhető támogatott programok.
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

- Aláírás jelenlétének és láncának gépi ellenőrzése a CI-ben.
- Időbélyeg és bináris hash változásának ellenőrzése.
- Negatív teszt: hibás, hiányzó vagy lejárt/revoked aláírásnál a release job
  álljon meg.
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

## Megvalósítási napló
Még nem indult el.
