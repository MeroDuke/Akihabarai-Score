import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSlider, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QComboBox,
    QMessageBox, QSpinBox
)

from app.scoring import clamp, tier_from_score, mixed_relevances, compute_score, normalize_ratios

APP_TITLE = "Akihabarai Score – Anime értékelő 1.0"

# A dropdown csak azt mondja meg, hány profilt használunk (1/2/3).
MIX_MODES = {
    "1 profil": 1,
    "2 profil": 2,
    "3 profil": 3,
}

TOTAL_WEIGHT = 100  # az aktív súlyok összege mindig ennyi legyen


DEFAULT_DIMENSIONS = [
    "Történet / plot",
    "Karakterek",
    "Pacing / epizódritmus",
    "Rendezés & vizuális történetmesélés",
    "Animáció & koreográfia",
    "Vizuális design",
    "Hang",
    "Hatás / élmény",
]

DEFAULT_TIERS = {
    "S": 9.0,
    "A": 8.0,
    "B": 7.0,
    "C": 6.0,
    "D": 5.0,
    "E": 4.0,
    "F": 1.0,
}


@dataclass
class DimState:
    name: str
    value: float = 5.0


def app_dir() -> str:
    # Works for dev and PyInstaller onefile
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_profiles_config() -> Tuple[List[str], Dict[str, List[float]], Dict[str, float], Optional[str]]:
    """
    Returns (dimensions, profiles, tier_thresholds, error_message)
    """
    cfg_path = os.path.join(app_dir(), "config", "profiles.json")
    if not os.path.exists(cfg_path):
        return DEFAULT_DIMENSIONS, {}, DEFAULT_TIERS, f"Hiányzik a config fájl: {cfg_path}"

    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        dims = data.get("dimensions") or DEFAULT_DIMENSIONS
        profiles = data.get("profiles") or {}
        tiers = data.get("tier_thresholds") or DEFAULT_TIERS

        # Basic validation
        if len(dims) != 8:
            return DEFAULT_DIMENSIONS, profiles, tiers, "A dimensions listának pontosan 8 eleműnek kell lennie."

        for pname, weights in profiles.items():
            if not isinstance(weights, list) or len(weights) != 8:
                return dims, {}, tiers, f"Hibás profil: '{pname}' (8 relevancia érték kell)."

        return dims, profiles, tiers, None

    except Exception as e:
        return DEFAULT_DIMENSIONS, {}, DEFAULT_TIERS, f"Nem sikerült beolvasni a profiles.json-t: {e}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE}")

        from PyQt6.QtGui import QIcon
        self.setWindowIcon(QIcon(os.path.join("assets", "icon.ico")))

        self.dimensions, self.profiles, self.tier_thresholds, err = load_profiles_config()

        self.states: List[DimState] = [DimState(n) for n in self.dimensions]
        self._building = True  # UI sync / programmatic changes guard

        root = QWidget()
        self.setCentralWidget(root)
        main = QHBoxLayout(root)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(16)

        # LEFT: inputs
        left_box = QGroupBox("Bevitel")
        left_layout = QVBoxLayout(left_box)
        left_layout.setSpacing(10)

        title_row = QHBoxLayout()
        title_lbl = QLabel("Anime / szezon cím:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("pl. Re:Zero S3")
        self.title_edit.textChanged.connect(self.recompute)
        title_row.addWidget(title_lbl)
        title_row.addWidget(self.title_edit, 1)
        left_layout.addLayout(title_row)

        # Profile controls
        prof_row = QGridLayout()
        prof_row.setHorizontalSpacing(10)
        prof_row.setVerticalSpacing(8)

        prof_row.addWidget(QLabel("Profil-mix mód:"), 0, 0)
        self.mix_combo = QComboBox()
        self.mix_combo.addItems(list(MIX_MODES.keys()))
        self.mix_combo.currentIndexChanged.connect(self.on_mix_changed)
        prof_row.addWidget(self.mix_combo, 0, 1, 1, 3)

        # Headings
        hdr_profile = QLabel("Profil")
        hdr_weight = QLabel("Súly (0–100)")
        hdr_profile.setStyleSheet("font-weight: 600;")
        hdr_weight.setStyleSheet("font-weight: 600;")
        prof_row.addWidget(QLabel(""), 1, 0)
        prof_row.addWidget(hdr_profile, 1, 1, 1, 2)
        prof_row.addWidget(hdr_weight, 1, 3)

        self.profile_combos: List[QComboBox] = []
        self.weight_spins: List[QSpinBox] = []

        self.profile_names: List[str] = list(self.profiles.keys())
        if not self.profile_names:
            self.profile_names = ["(nincs profil betöltve)"]

        for i in range(3):
            lbl = QLabel(f"Profil {i + 1}:")
            combo = QComboBox()
            combo.addItems(self.profile_names)
            combo.currentIndexChanged.connect(self.on_profile_changed)

            wspin = QSpinBox()
            wspin.setMinimum(0)
            wspin.setMaximum(TOTAL_WEIGHT)
            wspin.setSingleStep(1)
            wspin.setValue(0)

            # IMPORTANT: index capture must be idx=i, otherwise lambda bug
            wspin.valueChanged.connect(lambda v, idx=i: self.on_weight_changed(idx, v))

            self.profile_combos.append(combo)
            self.weight_spins.append(wspin)

            prof_row.addWidget(lbl, i + 2, 0)
            prof_row.addWidget(combo, i + 2, 1, 1, 2)
            prof_row.addWidget(wspin, i + 2, 3)

        left_layout.addLayout(prof_row)

        # Sliders grid
        self.slider_widgets: List[QSlider] = []
        self.spin_widgets: List[QDoubleSpinBox] = []

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        header_name = QLabel("Dimenzió")
        header_val = QLabel("Pont (0–10)")
        header_name.setStyleSheet("font-weight: 600;")
        header_val.setStyleSheet("font-weight: 600;")
        grid.addWidget(header_name, 0, 0)
        grid.addWidget(QLabel(""), 0, 1)
        grid.addWidget(header_val, 0, 2)

        for i, st in enumerate(self.states):
            row = i + 1
            name = QLabel(st.name)
            name.setWordWrap(True)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(10)
            slider.setMaximum(100)  # 0..10 with 0.1 steps
            slider.setValue(int(st.value * 10))
            slider.valueChanged.connect(lambda v, idx=i: self.on_slider_changed(idx, v))

            spin = QDoubleSpinBox()
            spin.setMinimum(1.0)
            spin.setMaximum(10.0)
            spin.setSingleStep(0.1)
            spin.setDecimals(1)
            spin.setValue(st.value)
            spin.valueChanged.connect(lambda v, idx=i: self.on_spin_changed(idx, v))

            self.slider_widgets.append(slider)
            self.spin_widgets.append(spin)

            grid.addWidget(name, row, 0)
            grid.addWidget(slider, row, 1)
            grid.addWidget(spin, row, 2)

        left_layout.addLayout(grid)

        btn_row = QHBoxLayout()
        self.reset_btn = QPushButton("Reset (5.0)")
        self.reset_btn.clicked.connect(self.reset_values)
        btn_row.addWidget(self.reset_btn)

        self.copy_btn = QPushButton("Másolás vágólapra")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_row.addWidget(self.copy_btn)

        left_layout.addLayout(btn_row)

        # RIGHT: result
        right_box = QGroupBox("Eredmény")
        right_layout = QVBoxLayout(right_box)
        right_layout.setSpacing(10)

        self.score_label = QLabel("— / 10")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSize(28)
        f.setBold(True)
        self.score_label.setFont(f)

        self.tier_label = QLabel("—")
        self.tier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf = QFont()
        tf.setPointSize(28)
        tf.setBold(True)
        self.tier_label.setFont(tf)

        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setStyleSheet("color: #666;")

        right_layout.addWidget(self.score_label)
        right_layout.addWidget(self.tier_label)
        right_layout.addWidget(self.summary_label)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Dimenzió", "Pont", "Relevancia", "Hozzájárulás"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.table, 1)

        main.addWidget(left_box, 3)
        main.addWidget(right_box, 2)

        self._building = False

        if err:
            QMessageBox.warning(self, "Config hiba", err)

        # Default: 1 profil → 100/0/0
        self._building = True
        self.weight_spins[0].setValue(TOTAL_WEIGHT)
        self.weight_spins[1].setValue(0)
        self.weight_spins[2].setValue(0)
        self._building = False

        # Apply initial mode + enforce unique dropdowns
        self.on_mix_changed()

    # ----------------------------
    # MIX MODE: enable/disable fields
    # ----------------------------
    def on_mix_changed(self):
        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

        self._building = True
        try:
            for i in range(3):
                enabled = i < needed
                self.profile_combos[i].setEnabled(enabled)
                self.weight_spins[i].setEnabled(enabled)
                if not enabled:
                    # inaktív sor: ne szóljon bele
                    self.weight_spins[i].setValue(0)
                    cb = self.profile_combos[i]
                    cb.blockSignals(True)
                    cb.clear()
                    cb.addItem("—")
                    cb.setCurrentIndex(0)
                    cb.blockSignals(False)
                else:
                    # ha újra aktív lesz, töltsük vissza a profilokat
                    cb = self.profile_combos[i]
                    cb.blockSignals(True)
                    cb.clear()
                    cb.addItems(list(self.profiles.keys()))
                    cb.blockSignals(False)

            # Ha aktív mezők összege 0, állítsunk értelmes alapot
            active_sum = sum(self.weight_spins[i].value() for i in range(needed))
            if active_sum <= 0:
                self.weight_spins[0].setValue(TOTAL_WEIGHT)
                for i in range(1, needed):
                    self.weight_spins[i].setValue(0)
            else:
                # Ha van már érték, akkor igazítsuk 100-ra (puffer logika)
                self._force_total_weight(needed, changed_idx=0)

            # Duplikált profilok kiszűrése (dropdown opciók frissítése)
            self._update_profile_combo_options_internal()

        finally:
            self._building = False

        self.recompute()

    # ----------------------------
    # PROFILE CHANGE: keep unique selections
    # ----------------------------
    def on_profile_changed(self):
        if self._building:
            return
        self._building = True
        try:
            self._update_profile_combo_options_internal()
        finally:
            self._building = False
        self.recompute()

    def _update_profile_combo_options_internal(self):
    #"""
    #- Az aktív sorokban a választás mindig egyedi legyen (nincs duplikáció).
    #- A duplikált aktív sor automatikusan átáll az első szabad profilra.
    #- A dropdownokban csak a még szabad profilok látszanak (plusz a saját aktuális).
    #"""
        if not self.profiles:
            return

        all_profiles = list(self.profiles.keys())
        if not all_profiles:
            return

        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

    # Jelenlegi kiválasztások
        current = [cb.currentText() for cb in self.profile_combos]

    # 1) Először kényszerítsünk ki egyedi kiválasztást az aktív sorokra
        used = set()
        chosen = [None, None, None]

        for i in range(needed):
            cur = current[i]
            if cur in all_profiles and cur not in used:
                chosen[i] = cur
                used.add(cur)
            else:
            # duplikált vagy invalid -> első szabad
                for p in all_profiles:
                    if p not in used:
                        chosen[i] = p
                        used.add(p)
                        break
            # ha valamiért nincs szabad (nagyon kevés profil esetén)
                if chosen[i] is None:
                    chosen[i] = all_profiles[0]

    # Inaktív sorokra: legyen valami “ártatlan” érték (nem számít a scoringban)
        for i in range(needed, 3):
            chosen[i] = all_profiles[0]

    # 2) Most frissítsük a combókat úgy, hogy csak a szabad opciók jelenjenek meg
        for i, combo in enumerate(self.profile_combos):
            # Inaktív sorokhoz ne nyúljunk (ott maradjon a "—")
            if i >= needed:
                continue
        # más aktív sorok által foglalt profilok:
            other_used = set(chosen[:needed])
            if i < needed:
                other_used.discard(chosen[i])  # a sajátját hagyjuk meg

            allowed = []
            for p in all_profiles:
                if p == chosen[i] or p not in other_used:
                    allowed.append(p)

            combo.blockSignals(True)
            combo.clear()
            combo.addItems(allowed)
            combo.setCurrentText(chosen[i])
            combo.blockSignals(False)

    # ----------------------------
    # WEIGHT AUTO-BALANCE
    # ----------------------------
    def on_weight_changed(self, changed_idx: int, new_value: int):
        if self._building:
            return

        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

        if changed_idx >= needed:
            return

        self._building = True
        try:
            self._force_total_weight(needed, changed_idx=changed_idx)
        finally:
            self._building = False

        self.recompute()

    def _force_total_weight(self, needed: int, changed_idx: int):
        """
        Puffer-elv:
        - Alap puffer: az utolsó aktív mező (needed-1).
        - Ha pont a puffert tekered, akkor az első mező lesz a puffer.
        Cél: aktív mezők összege = TOTAL_WEIGHT.
        """
        spins = self.weight_spins[:needed]
        if needed <= 1:
            spins[0].setValue(TOTAL_WEIGHT)
            return

        buffer_idx = needed - 1
        if changed_idx == buffer_idx:
            buffer_idx = 0  # ha a puffert tekerik, az első lesz a puffer

        # Sum "minden más" a puffer kivételével
        others_sum = 0
        for i, sp in enumerate(spins):
            if i == buffer_idx:
                continue
            others_sum += int(sp.value())

        buffer_value = TOTAL_WEIGHT - others_sum

        if buffer_value >= 0:
            spins[buffer_idx].setValue(buffer_value)
            return

        # Túlmentünk 100-on: puffer = 0 és a "changed" mezőt visszafogjuk max-ra
        spins[buffer_idx].setValue(0)

        fixed_sum = 0
        for i, sp in enumerate(spins):
            if i in (buffer_idx, changed_idx):
                continue
            fixed_sum += int(sp.value())

        max_for_changed = TOTAL_WEIGHT - fixed_sum
        if max_for_changed < 0:
            max_for_changed = 0

        current = int(spins[changed_idx].value())
        if current > max_for_changed:
            spins[changed_idx].setValue(max_for_changed)

    # ----------------------------
    # Dimension inputs
    # ----------------------------
    def on_slider_changed(self, idx: int, v: int):
        if self._building:
            return
        self._building = True
        value = v / 10.0
        self.states[idx].value = value
        self.spin_widgets[idx].setValue(value)
        self._building = False
        self.recompute()

    def on_spin_changed(self, idx: int, v: float):
        if self._building:
            return
        self._building = True
        self.states[idx].value = float(v)
        self.slider_widgets[idx].setValue(int(round(v * 10)))
        self._building = False
        self.recompute()

    def reset_values(self):
        self._building = True
        for i in range(len(self.states)):
            self.states[i].value = 5.0
            self.slider_widgets[i].setValue(50)
            self.spin_widgets[i].setValue(5.0)
        self._building = False
        self.recompute()

    # ----------------------------
    # Scoring
    # ----------------------------
    def get_selected_profiles_and_ratios(self) -> Tuple[List[str], List[float]]:
        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

        selected: List[str] = []
        weights: List[float] = []

        for i in range(needed):
            selected.append(self.profile_combos[i].currentText())
            weights.append(float(self.weight_spins[i].value()))

        ratios = normalize_ratios(weights)
        return selected, ratios

    def recompute(self):
        selected, ratios = self.get_selected_profiles_and_ratios()
        rel = mixed_relevances(self.profiles, selected, ratios)

        vals = [s.value for s in self.states]
        score, used_rel, contrib = compute_score(vals, rel)

        score_for_tier = round(score, 3)
        tier = tier_from_score(score_for_tier, self.tier_thresholds)

        from app.scoring import display_score_consistent
        display_score = display_score_consistent(
            score,
            tier,
            self.tier_thresholds
        )

        self.score_label.setText(f"{display_score:.1f} / 10")
        self.tier_label.setText(f"Tier: {tier}")

        values = [(i, self.states[i].value) for i in range(8)]
        values_sorted = sorted(values, key=lambda x: x[1], reverse=True)
        top2 = values_sorted[:2]
        low1 = values_sorted[-1]

        top_str = ", ".join([f"{self.states[i].name} ({v:.1f})" for i, v in top2])
        low_str = f"{self.states[low1[0]].name} ({low1[1]:.1f})"

        title = self.title_edit.text().strip()
        if title:
            self.summary_label.setText(f"{title}\nErősségek: {top_str}\nGyengeség: {low_str}")
        else:
            self.summary_label.setText(f"Erősségek: {top_str}\nGyengeség: {low_str}")

        self.update_table(used_rel, contrib)

    def update_table(self, rel: List[float], contrib: List[float]):
        self.table.setRowCount(8)
        for r in range(8):
            name = self.states[r].name
            val = self.states[r].value
            w = rel[r]
            c = contrib[r]

            items = [
                QTableWidgetItem(name),
                QTableWidgetItem(f"{val:.1f}"),
                QTableWidgetItem(f"{w:.2f}"),
                QTableWidgetItem(f"{c:.2f}")
            ]
            items[0].setToolTip(name)
            for cidx, it in enumerate(items):
                if cidx in (1, 2, 3):
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(r, cidx, it)

    def copy_to_clipboard(self):
        title = self.title_edit.text().strip() or "(nincs cím)"
        selected, ratios = self.get_selected_profiles_and_ratios()
        rel = mixed_relevances(self.profiles, selected, ratios)

        vals = [s.value for s in self.states]
        score, _, _ = compute_score(vals, rel)
        tier = tier_from_score(score, self.tier_thresholds)

        prof_part = " + ".join([f"{p} ({int(round(r * 100))}%)" for p, r in zip(selected, ratios)])

        lines = [f"{title} — {score:.1f}/10 (Tier {tier})", f"Profil: {prof_part}", ""]
        for s in self.states:
            lines.append(f"- {s.name}: {s.value:.1f}")
        text = "\n".join(lines)

        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Másolva", "Az összegzés a vágólapra került.")


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(1200, 720)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()