# Akihabarai Score

🎬 Anime értékelő alkalmazás az Akihabarai Könyvespolc pontozási rendszeréhez.

**Gyors kezdés:**

1. Töltsd le a legfrissebb verziót a **Releases** oldalról  
2. Csomagold ki a ZIP fájlt  
3. Indítsd el az `AkihabaraiScore.exe` fájlt

---

Az **Akihabarai Score** az Akihabarai Könyvespolc YouTube csatornán használt  
8 dimenziós anime értékelési rendszer hivatalos alkalmazása.

A program célja, hogy átláthatóvá tegye a szezonvégi értékelések mögötti számítási logikát,  
és lehetővé tegye, hogy bárki ugyanazt a rendszert használja.

⚠️ A projekt jelenleg fejlesztés alatt áll (**pre-1.0 állapot**).

---

## 🎯 Hogyan működik?

Az értékelés **8 fix dimenzión** alapul:

- Történet / plot
- Karakterek
- Tempó / epizódrítmus
- Rendezés & vizuális történetmesélés
- Animáció & koreográfia
- Vizuális dizájn
- Hang
- Hatás / élmény

Minden dimenzió **1.0–10.0 skálán értékelhető**.

A végső pontszám **súlyozott átlag** alapján számolódik,  
a kiválasztott műfaji profilok relevanciája szerint.

A rendszer **nem bünteti azt, ami nincs jelen egy műben** –  
csak azt értékeli, ami releváns az adott fókuszhoz.

---

## 🧠 Mit számol a program?

A végső pontszám képlete:

```
Σ (dimenzió × relevancia) / Σ (relevancia)
```

Az alkalmazás automatikusan megjeleníti:

- a **végső pontszámot** (0–10)
- a **tier besorolást** (S–F)
- a **legerősebb dimenziókat**
- a **leggyengébb dimenziókat**
- a **részletes pontozási bontást**

---

## 🎭 Profilok és súlyozás

A különböző műfajok más szempontokat helyeznek előtérbe, ezért az alkalmazás  
**profil alapú súlyozást** használ.

A felhasználó választhat:

- **1 profilt**
- **2 profil keverését**
- **3 profil keverését**

A kiválasztott profilok határozzák meg, hogy a különböző dimenziók milyen súllyal  
számítanak bele a végső pontszámba.

---

## 💻 Használat

### Windows (ajánlott)

1. Töltsd le a legfrissebb verziót a **Releases** menüpontból.
2. Csomagold ki a ZIP fájlt.
3. Futtasd az `AkihabaraiScore.exe` fájlt.

⚠️ Mivel az alkalmazás nincs digitálisan aláírva,  
a Windows SmartScreen figyelmeztetést jeleníthet meg.

Ilyenkor kattints:

**„További információ” → „Futtatás mindenképp”**

---

## 📋 Eredmény exportálása

Az alkalmazás az értékelést több formátumban is ki tudja adni.

### Szöveges eredmény

Az értékelés **vágólapra másolható szövegként**, így könnyen megosztható például:

- Discordon
- fórumokon
- közösségi médiában

### Eredménykártya kép

Az értékelés **képként is generálható**, amely ideális:

- közösségi médiához
- YouTube tartalmakhoz
- vizuális megosztáshoz

---

## 📊 Tier besorolás

A végső pontszám automatikusan tier kategóriába kerül:

- **S** – kivételes  
- **A** – kiemelkedő  
- **B** – erős  
- **C** – átlag feletti  
- **D** – átlagos  
- **E** – gyenge  
- **F** – rossz  

---

## ⚠️ Projekt állapota

A program jelenleg **1.0 előtti állapotban van**, ezért:

- a felület még változhat
- új funkciók kerülhetnek be
- kisebb módosítások előfordulhatnak