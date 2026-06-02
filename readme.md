# ✨ Akihabarai Score

🎌 Anime értékelő alkalmazás az Akihabarai Könyvespolc pontozási rendszeréhez.

Az **Akihabarai Score** az Akihabarai Könyvespolc YouTube csatornán használt, **8 dimenziós anime értékelési rendszer** hivatalos alkalmazása. A program célja, hogy egységes, átlátható és újrahasználható formában tegye elérhetővé ugyanazt a pontozási logikát, amely a csatornán is megjelenik.

🚀 A projekt már **közel jár az 1.0-s állapothoz**: a fő funkciók működnek, a felület magyar, az értékelési logika stabil, és az alkalmazás tesztekkel, valamint automatikus build folyamattal is meg van támogatva.

------------------------------------------------------------------------

## 🎯 Mire való a program?

Az alkalmazás segítségével egy anime, évad vagy szezonpontozás gyorsan és egységes logika mentén elkészíthető.

A rendszer nem pusztán átlagot számol, hanem figyelembe veszi, hogy az adott műfajban **mely dimenziók mennyire fontosak**. Emiatt ugyanaz a pontszámkészlet más végeredményt adhat például egy akció- vagy egy romantikus címnél.

💡 A cél nem az, hogy minden művet ugyanazzal a sablonnal büntessen vagy jutalmazzon, hanem hogy az értékelés az adott fókuszhoz igazodjon.

------------------------------------------------------------------------

## 🧠 Az értékelés alapja

A program **8 fix dimenziót** használ:

- 📖 Történet / plot
- 👥 Karakterek
- ⏱️ Tempó / epizódrítmus
- 🎬 Rendezés & vizuális történetmesélés
- 💥 Animáció & koreográfia
- 🎨 Vizuális dizájn
- 🔊 Hang
- 💭 Hatás / élmény

Minden dimenzió **1,0 és 10,0** között pontozható.

A végső pontszám súlyozott átlag alapján készül:

    Σ (dimenzió × relevancia) / Σ (relevancia)

------------------------------------------------------------------------

## ⚖️ Profilalapú súlyozás

Az alkalmazás jelenleg **10 profilt** tartalmaz:

- 🐉 Fantasy
- 🕵️ Rejtély
- ❤️ Romantika
- 🎭 Dráma
- ⚔️ Akció
- 🧭 Kaland
- 😂 Humor
- 🏡 Mindennapi Élet
- 🚀 Sci-fi
- 👻 Horror

A felhasználó választhat:

- **1 profilt**
- **2 profil keverését**
- **3 profil keverését**

A profilokhoz külön súly adható, amelyek összege mindig **100%**. A program ezt automatikusan kezeli.

💡 Fontos elv: a rendszer **nem azt kéri számon, ami nincs jelen egy műben**, hanem azt nézi, hogy az adott profil szerint mi számít igazán relevánsnak.

------------------------------------------------------------------------

## 📊 Mit mutat az alkalmazás?

Az értékelés után a program automatikusan megjeleníti:

- ⭐ a **végső pontszámot**
- 🏷️ a **tier besorolást**
- 💪 az adott értékelés **erősségeit**
- ⚠️ a leggyengébb dimenziót
- 📋 a **részletes bontást táblázatban**
- 📈 a dimenziónkénti **relevanciát**
- 🧮 a dimenziónkénti **hozzájárulást**

------------------------------------------------------------------------

## 🏆 Tier rendszer

A program a végeredményt automatikusan tier kategóriába sorolja:

- 🟣 **S** -- Kiváló
- 🔵 **A** -- Nagyon jó
- 🟢 **B** -- Jó
- ⚪ **C** -- Átlagos
- 🟡 **D** -- Elmegy
- 🟠 **E** -- Elégséges
- 🔴 **F** -- Elégtelen

A kijelzett pontszám és a tier egymással konzisztens marad.

------------------------------------------------------------------------

## 🧱 Tier lista rendszer

Az alkalmazás képes több anime értékelésének egyidejű kezelésére is.

A felhasználó a jelenlegi eredményt egyetlen gombnyomással hozzáadhatja a beépített Tier listához.

A rendszer:

- 🏷️ automatikusan a megfelelő tier sorba helyezi az értékelést
- 👀 élő preview-t mutat a jelenlegi eredményről
- ❌ lehetővé teszi mentett kártyák eltávolítását
- 🚫 megakadályozza az üres vagy duplikált címek hozzáadását
- 📦 futásidőben memóriában tárolja a Tier listát

💡 A Tier lista jelenleg session alapú.

Ez azt jelenti, hogy az alkalmazás bezárásakor minden mentett Tier kártya törlődik.

------------------------------------------------------------------------

## 📤 Export és megosztás

Az alkalmazás többféle gyors megosztást támogat.

### 📋 1. Részletes szöveg másolása vágólapra

A program egy formázott, könnyen beilleszthető szöveget készít, amely használható például:

- Discordon
- fórumokon
- közösségi médiában
- jegyzeteléshez

### 🖼️ 2. Eredménykártya másolása képként

Az eredmény egy különálló vizuális kártyaként is vágólapra másolható:

- YouTube tartalmakban
- közösségi posztokban
- thumbnail alapjaként

### 🏆 3. Tier lista másolása képként

A teljes Tier lista egyetlen képként is vágólapra másolható.

Az export során:

- a preview kártya automatikusan elrejtésre kerül
- a törlés gombok nem jelennek meg
- a lista tiszta, megosztható formában kerül másolásra

Ez különösen hasznos:

- szezonos anime összesítéseknél
- toplisták készítésénél
- közösségi megosztásoknál
- YouTube videókban vagy thumbnail alapként

------------------------------------------------------------------------

## 🖥️ Felület és használhatóság

A jelenlegi verzióban az alkalmazás több fontos kényelmi fejlesztést kapott:

- 🇭🇺 teljesen magyar nyelvű felület
- 🌗 sötét és világos rendszer-téma jobb kezelése
- 🧱 integrált Tier lista rendszer
- 📦 ikonkezelés és hordozható EXE csomagolás
- ⚙️ külön konfigurációs fájlok

A program csak Windowsra lett lefejlesztve és használatra kész állapotban csomagolt formában érhető el.

------------------------------------------------------------------------

## 🌐 AniList integráció

Az alkalmazás opcionális AniList integrációt is tartalmaz.

Funkciók:

- anime címkeresés online adatbázisból
- automatikus címjavaslatok
- borítókép megjelenítés Tier kártyákon

Az integráció teljesen opcionális, az alkalmazás nélküle is használható.

Az AniListből lekért adatok nem kerülnek helyi adatbázisba vagy gyorsítótárba mentésre, és nem maradnak meg az alkalmazás bezárása után.

------------------------------------------------------------------------

## 🧾 Naplózás és hibakeresés

Az alkalmazás részletes naplófájlokat tud készíteni a `logs` mappába.

🔍 Ez különösen hasznos, ha valami nem a várt módon működik, és vissza kell követni az eseményeket.

A logger képes többek között rögzíteni:

- alkalmazásindítást
- UI eseményeket
- Tier lista műveleteket
- export folyamatokat
- hibákat és figyelmeztetéseket

------------------------------------------------------------------------

## 🐞 Hibajelentés

Ha hibát találsz, kérlek a GitHub-on jelezd:

👉 https://github.com/MeroDuke/Akihabarai-Score/issues

A gyorsabb és pontosabb megoldás érdekében érdemes az alábbiakat mellékelni:

- 📌 rövid leírás a problémáról
- 🔁 reprodukció lépései (hogyan lehet előidézni)
- 📂 a `logs` mappából releváns naplófájl
- 🖥️ opcionálisan képernyőkép

📎 A GitHub issue-hoz fájlok is csatolhatók, így a logok feltöltése egyszerűen megoldható.

------------------------------------------------------------------------

## ⚙️ Jelenlegi projektállapot

- 🧩 moduláris pontozási logika
- 🔀 stabil profilkeverés
- 🏆 Tier lista rendszer
- 📋 vágólapos export
- 🖼️ Tier lista kép export
- 🎴 eredménymegjelenítés külön service-ben
- 🧾 részletes naplózás
- 📦 rendezett EXE build
- 🧪 automatizált tesztek
- 🧪 UI widget tesztek
- 🤖 GitHub Actions CI/CD

------------------------------------------------------------------------

## ⚠️ Fontos megjegyzés

Mivel az alkalmazás nincs digitálisan aláírva, a Windows SmartScreen figyelmeztetést jeleníthet meg első indításkor.

Ilyenkor a következő útvonalon lehet továbblépni:

➡️ **„További információ" → „Futtatás mindenképp"**

------------------------------------------------------------------------

## 🧭 Összefoglalás

Az **Akihabarai Score** egy olyan célprogram, amely az Akihabarai Könyvespolc saját anime értékelési rendszerét teszi használhatóvá mások számára is.

🎯 A hangsúly:

- átlátható pontozás
- műfaji érzékenység
- gyors megoszthatóság
- Tier alapú vizuális rendszerezés
- stabil, gyakorlatban használható működés

