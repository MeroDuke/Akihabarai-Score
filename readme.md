# Akihabarai Score

Az **Akihabarai Score** az Akihabarai Könyvespolc YouTube csatornán használt,
8 dimenziós anime értékelési rendszer hivatalos alkalmazása.

A program célja, hogy átláthatóvá tegye a szezonvégi értékelések mögötti
számítási logikát, és lehetővé tegye, hogy bárki ugyanazt a rendszert használja.

⚠️ A projekt jelenleg fejlesztés alatt áll (pre-1.0 állapot).

---

## 🎯 Hogyan működik?

Az értékelés 8 fix dimenzión alapul:

- Történet / plot
- Karakterek
- Tempó / epizódrítmus
- Rendezés & vizuális történetmesélés
- Animáció & koreográfia
- Vizuális dizájn
- Hang
- Hatás / élmény

Minden dimenzió 0–10 skálán értékelhető.

A végső pontszám súlyozott átlag alapján számolódik,
a kiválasztott műfaji tagek (pl. Akció, Dráma, Fantasy stb.) relevanciája szerint.

A rendszer nem bünteti azt, ami nincs jelen egy műben –
csak azt értékeli, ami releváns az adott fókuszhoz.

---

## 🧠 Mit számol a program?

A végső pontszám képlete:

Σ (dimenzió × relevancia) / Σ (relevancia)

Az alkalmazás megjeleníti:

- végső pontszám (0–10)
- besorolás (S–F)
- legerősebb és leggyengébb dimenziók
- részletes bontás

---

## 💻 Használat

### Windows (ajánlott)

1. Töltsd le a legfrissebb verziót a Releases menüpontból.
2. Csomagold ki a ZIP fájlt.
3. Futtasd az `AkihabaraiScore.exe` fájlt.

⚠️ Mivel az alkalmazás nincs digitálisan aláírva,
a Windows SmartScreen figyelmeztetést jeleníthet meg.

Ilyenkor kattints:
**„További információ” → „Futtatás mindenképp”**

---

## 🛠 Fejlesztői futtatás

Ha Pythonból szeretnéd futtatni:

```bash
pip install -r requirements.txt
python app/main.py
