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
    QMessageBox
)

APP_TITLE = "Akihabarai Score – Anime értékelő 1.0"

MIX_PRESETS = {
    "100% (egy profil)": [1.0],
    "70 / 30": [0.7, 0.3],
    "60 / 40": [0.6, 0.4],
    "50 / 50": [0.5, 0.5],
    "50 / 30 / 20": [0.5, 0.3, 0.2],
}

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


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def tier_from_score(score: float, thresholds: Dict[str, float]) -> str:
    # Expect thresholds like {"S":9.0,"A":8.0,...,"F":1.0}
    # Return highest tier whose threshold <= score
    order = ["S", "A", "B", "C", "D", "E", "F"]
    for t in order:
        if score >= float(thresholds.get(t, 0.0)):
            return t
    return "F"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE}")

        from PyQt6.QtGui import QIcon
        self.setWindowIcon(QIcon(os.path.join("assets", "icon.ico")))

        self.dimensions, self.profiles, self.tier_thresholds, err = load_profiles_config()

        self.states: List[DimState] = [DimState(n) for n in self.dimensions]
        self._building = True

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

        prof_row.addWidget(QLabel("Profil-mix preset:"), 0, 0)
        self.mix_combo = QComboBox()
        self.mix_combo.addItems(list(MIX_PRESETS.keys()))
        self.mix_combo.currentIndexChanged.connect(self.on_mix_changed)
        prof_row.addWidget(self.mix_combo, 0, 1, 1, 2)

        self.profile_combos: List[QComboBox] = []
        profile_names = list(self.profiles.keys())
        if not profile_names:
            profile_names = ["(nincs profil betöltve)"]

        for i in range(3):
            lbl = QLabel(f"Profil {i+1}:")
            combo = QComboBox()
            combo.addItems(profile_names)
            combo.currentIndexChanged.connect(self.recompute)
            self.profile_combos.append(combo)
            prof_row.addWidget(lbl, i + 1, 0)
            prof_row.addWidget(combo, i + 1, 1, 1, 2)

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
            slider.setMinimum(0)
            slider.setMaximum(100)  # 0..10 with 0.1 steps
            slider.setValue(int(st.value * 10))
            slider.valueChanged.connect(lambda v, idx=i: self.on_slider_changed(idx, v))

            spin = QDoubleSpinBox()
            spin.setMinimum(0.0)
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
        tf.setPointSize(28)      # ugyanakkora, mint a score
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

        self.on_mix_changed()
        self.recompute()

    def on_mix_changed(self):
        # Enable only as many profile selectors as the preset needs
        preset = self.mix_combo.currentText()
        ratios = MIX_PRESETS.get(preset, [1.0])
        needed = len(ratios)
        for i, combo in enumerate(self.profile_combos):
            combo.setEnabled(i < needed)
        self.recompute()

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

    def get_selected_profiles_and_ratios(self) -> Tuple[List[str], List[float]]:
        preset = self.mix_combo.currentText()
        ratios = MIX_PRESETS.get(preset, [1.0])

        selected = []
        for i in range(len(ratios)):
            selected.append(self.profile_combos[i].currentText())

        # Normalize ratios in case
        s = sum(ratios)
        if s <= 0:
            ratios = [1.0] + [0.0] * (len(ratios) - 1)
        else:
            ratios = [r / s for r in ratios]

        return selected, ratios

    def mixed_relevances(self) -> Optional[List[float]]:
        if not self.profiles:
            return None

        selected, ratios = self.get_selected_profiles_and_ratios()
        rel = [0.0] * 8
        for pname, r in zip(selected, ratios):
            weights = self.profiles.get(pname)
            if not weights:
                continue
            for i in range(8):
                rel[i] += float(weights[i]) * float(r)

        # Clamp to [0.0, 1.0] for safety (your spec is 0.2–1.0)
        rel = [clamp(x, 0.0, 1.0) for x in rel]
        return rel

    def compute_score(self) -> Tuple[float, List[float], List[float]]:
        """
        Returns: (final_score_1to10, relevances, contributions)
        final_score is weighted average:
          Σ(dim * rel) / Σ(rel)
        """
        rel = self.mixed_relevances()
        if rel is None:
            # fallback: simple average
            vals = [s.value for s in self.states]
            score = sum(vals) / len(vals) if vals else 0.0
            return score, [1.0] * 8, vals

        num = 0.0
        den = 0.0
        contrib = []
        for s, w in zip(self.states, rel):
            c = s.value * w
            contrib.append(c)
            num += c
            den += w

        score = (num / den) if den > 0 else 0.0
        return score, rel, contrib

    def recompute(self):
        score, rel, contrib = self.compute_score()
        score = clamp(score, 0.0, 10.0)

        tier = tier_from_score(score, self.tier_thresholds)
        self.score_label.setText(f"{score:.1f} / 10")
        self.tier_label.setText(f"Tier: {tier}")

        # Strength/weakness (by raw value, not by contribution)
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

        self.update_table(rel, contrib)

    def update_table(self, rel: List[float], contrib: List[float]):
        self.table.setRowCount(8)
        for r in range(8):
            name = self.states[r].name
            val = self.states[r].value
            w = rel[r]
            c = contrib[r]

            # Simple note: highlight highest and lowest
            note = ""
            # We'll mark only absolute best/worst by raw value for readability
            vals = [s.value for s in self.states]
            if val == max(vals):
                note = "MAX"
            if val == min(vals):
                note = "MIN"

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
        score, _, _ = self.compute_score()
        score = clamp(score, 0.0, 10.0)
        tier = tier_from_score(score, self.tier_thresholds)

        selected, ratios = self.get_selected_profiles_and_ratios()
        prof_part = " + ".join([f"{p} ({int(r*100)}%)" for p, r in zip(selected, ratios)])

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
