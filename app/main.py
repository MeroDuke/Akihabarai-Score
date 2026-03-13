import sys
import html
import ctypes
from typing import Dict, List, Tuple, Optional

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QGuiApplication, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSlider, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QComboBox,
    QMessageBox, QSpinBox, QSizePolicy
)

from app.core.constants import APP_TITLE, MIX_MODES, TOTAL_WEIGHT
from app.core.models import DimState
from app.core.runtime import load_app_icon
from app.config.ui_config import load_ui_config
from app.config.profiles_config import load_profiles_config
from app.scoring import (
    tier_from_score,
    mixed_relevances,
    compute_score,
    normalize_ratios,
    display_score_consistent,
)
from app.logger import init_logger, log_debug, log_info, log_warning

from app.services.clipboard_service import (
    copy_text_to_clipboard,
    copy_widget_as_pixmap,
)

from app.services.profile_mix_service import (
    get_selected_profiles_and_ratios,
    force_total_weight,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE}")

        self.dimensions, self.profiles, self.tier_thresholds, err = load_profiles_config()
        self.ui_cfg, ui_err = load_ui_config()

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

        # ----------------------------
        # Top rows aligned to the same "grid"
        # ----------------------------
        top_label_w = 140
        top_num_w = 80  # csak a ritmus miatt (üresen hagyjuk itt)

        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(10)
        top_grid.setVerticalSpacing(8)

        top_grid.setColumnMinimumWidth(0, top_label_w)
        top_grid.setColumnStretch(1, 1)
        top_grid.setColumnMinimumWidth(2, top_num_w)

        # Row 0: Title
        title_lbl = QLabel("Anime / szezon cím:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("pl. Re:Zero S3")
        self.title_edit.textChanged.connect(self.recompute)

        top_grid.addWidget(title_lbl, 0, 0)
        top_grid.addWidget(self.title_edit, 0, 1)
        top_grid.addWidget(QLabel(""), 0, 2)

        # Row 1: Mix mode
        mix_lbl = QLabel("Profil-mix mód:")
        self.mix_combo = QComboBox()
        self.mix_combo.addItems(list(MIX_MODES.keys()))
        self.mix_combo.currentIndexChanged.connect(self.on_mix_changed)

        top_grid.addWidget(mix_lbl, 1, 0)
        top_grid.addWidget(self.mix_combo, 1, 1)
        top_grid.addWidget(QLabel(""), 1, 2)

        left_layout.addLayout(top_grid)

        # Profile selection + weights in a dedicated group box.
        profiles_group = QGroupBox("Profil konfiguráció")
        profiles_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        prof_row = QGridLayout(profiles_group)
        prof_row.setColumnMinimumWidth(0, 130)
        prof_row.setColumnMinimumWidth(1, 220)
        prof_row.setColumnMinimumWidth(3, 80)
        prof_row.setColumnStretch(1, 1)
        prof_row.setHorizontalSpacing(10)
        prof_row.setVerticalSpacing(6)

        hdr_profile = QLabel("Profil")
        hdr_weight = QLabel("Súly (0-100)")
        hdr_profile.setStyleSheet("font-weight: 600;")
        hdr_weight.setStyleSheet("font-weight: 600;")
        prof_row.addWidget(QLabel(""), 0, 0)
        prof_row.addWidget(hdr_profile, 0, 1, 1, 2)
        prof_row.addWidget(hdr_weight, 0, 3)

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
            wspin.valueChanged.connect(lambda v, idx=i: self.on_weight_changed(idx, v))

            self.profile_combos.append(combo)
            self.weight_spins.append(wspin)

            prof_row.addWidget(lbl, i + 1, 0)
            prof_row.addWidget(combo, i + 1, 1, 1, 2)
            prof_row.addWidget(wspin, i + 1, 3)

        for r in range(0, 4):
            prof_row.setRowStretch(r, 0)

        left_layout.addWidget(profiles_group)

        # Sliders grid
        self.slider_widgets: List[QSlider] = []
        self.spin_widgets: List[QDoubleSpinBox] = []

        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 130)
        grid.setColumnMinimumWidth(2, 80)
        grid.setColumnStretch(1, 1)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        header_name = QLabel("Dimenzió")
        header_val = QLabel("Pont (1-10)")
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
            slider.setMaximum(100)
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

        dims_group = QGroupBox("Dimenziók")
        dims_layout = QVBoxLayout(dims_group)
        dims_layout.setContentsMargins(12, 10, 12, 10)
        dims_layout.setSpacing(10)
        grid.setVerticalSpacing(10)
        dims_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        dims_layout.addLayout(grid)
        dims_layout.addStretch(1)
        left_layout.addWidget(dims_group, 1)

        btn_row = QHBoxLayout()

        self.reset_btn = QPushButton("Reset (5.0)")
        self.reset_btn.clicked.connect(self.reset_values)
        self.reset_btn.setFixedHeight(30)
        btn_row.addWidget(self.reset_btn)

        self.copy_btn = QPushButton("Részletes adatok másolása vágólapra")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setFixedHeight(30)
        btn_row.addWidget(self.copy_btn)

        style = self.style()
        self.copy_btn.setIcon(style.standardIcon(style.StandardPixmap.SP_FileIcon))
        self.copy_btn.setIconSize(QSize(16, 16))

        left_layout.addLayout(btn_row)

        # RIGHT: result
        self.right_box = QGroupBox("Eredmény")
        right_box = self.right_box
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
        self.summary_label.setStyleSheet("")
        self.summary_label.setTextFormat(Qt.TextFormat.RichText)

        self.result_card = QWidget()
        card_layout = QVBoxLayout(self.result_card)
        self.result_card.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Maximum,
        )
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(0, 0, 0, 0)

        card_layout.addWidget(self.score_label)
        card_layout.addWidget(self.tier_label)
        card_layout.addWidget(self.summary_label)

        right_layout.addWidget(self.result_card, alignment=Qt.AlignmentFlag.AlignCenter)

        self.copy_img_btn = QPushButton("Eredmény másolása vágólapra")
        self.copy_img_btn.setFixedHeight(32)
        self.copy_img_btn.clicked.connect(self.copy_result_image_to_clipboard)
        right_layout.addWidget(self.copy_img_btn)

        self.copy_img_btn.setIcon(
            style.standardIcon(style.StandardPixmap.SP_FileDialogListView)
        )
        self.copy_img_btn.setIconSize(QSize(16, 16))

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Dimenzió", "Pont", "Relevancia", "Hozzájárulás"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for c in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents
            )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.table, 1)

        main.addWidget(left_box, 3)
        main.addWidget(right_box, 2)

        self._building = False

        log_info(
            "config",
            f"Loaded profiles: dims={len(self.dimensions)}, profiles={len(self.profiles)}",
        )
        if err:
            log_warning("config", f"profiles.json issue: {err}")

        log_info("config", "Loaded UI config")
        if ui_err:
            log_warning("config", f"ui.json issue: {ui_err}")

        if err:
            QMessageBox.warning(self, "Config hiba", err)

        if ui_err:
            QMessageBox.warning(self, "UI config hiba", ui_err)

        self._building = True
        self.weight_spins[0].setValue(TOTAL_WEIGHT)
        self.weight_spins[1].setValue(0)
        self.weight_spins[2].setValue(0)
        self._building = False

        self.on_mix_changed()

    def on_mix_changed(self):
        mode = self.mix_combo.currentText()
        log_info("ui", f"mix_mode_changed: mode='{mode}'")
        needed = MIX_MODES.get(mode, 1)

        self._building = True
        try:
            for i in range(3):
                enabled = i < needed
                self.profile_combos[i].setEnabled(enabled)
                self.weight_spins[i].setEnabled(enabled)

                if not enabled:
                    self.weight_spins[i].setValue(0)
                    cb = self.profile_combos[i]
                    cb.blockSignals(True)
                    cb.clear()
                    cb.addItem("—")
                    cb.setCurrentIndex(0)
                    cb.blockSignals(False)
                else:
                    cb = self.profile_combos[i]
                    cb.blockSignals(True)
                    cb.clear()
                    cb.addItems(list(self.profiles.keys()))
                    cb.blockSignals(False)

            active_sum = sum(self.weight_spins[i].value() for i in range(needed))
            if active_sum <= 0:
                self.weight_spins[0].setValue(TOTAL_WEIGHT)
                for i in range(1, needed):
                    self.weight_spins[i].setValue(0)
            else:
                force_total_weight(self.weight_spins, needed, 0)

            self._update_profile_combo_options_internal()
        finally:
            self._building = False

        self.recompute()

    def on_profile_changed(self):
        if self._building:
            return

        self._building = True
        selected, ratios = get_selected_profiles_and_ratios(
            self.profile_combos,
            self.weight_spins,
            self.mix_combo.currentText(),
            MIX_MODES,
        )
        log_info("ui", f"profile_changed: selected={selected} ratios={ratios}")
        try:
            self._update_profile_combo_options_internal()
        finally:
            self._building = False

        self.recompute()

    def _update_profile_combo_options_internal(self):
        if not self.profiles:
            return

        all_profiles = list(self.profiles.keys())
        if not all_profiles:
            return

        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

        current = [cb.currentText() for cb in self.profile_combos]

        used = set()
        chosen: List[Optional[str]] = [None, None, None]

        for i in range(needed):
            cur = current[i]
            if cur in all_profiles and cur not in used:
                chosen[i] = cur
                used.add(cur)
            else:
                for p in all_profiles:
                    if p not in used:
                        chosen[i] = p
                        used.add(p)
                        break
                if chosen[i] is None:
                    chosen[i] = all_profiles[0]

        for i in range(needed, 3):
            chosen[i] = all_profiles[0]

        for i, combo in enumerate(self.profile_combos):
            if i >= needed:
                continue

            other_used = set(chosen[:needed])
            other_used.discard(chosen[i])

            allowed = []
            for p in all_profiles:
                if p == chosen[i] or p not in other_used:
                    allowed.append(p)

            combo.blockSignals(True)
            combo.clear()
            combo.addItems(allowed)
            combo.setCurrentText(chosen[i] or all_profiles[0])
            combo.blockSignals(False)

    def on_weight_changed(self, changed_idx: int, new_value: int):
        if self._building:
            return

        log_info("ui", f"weight_changed: idx={changed_idx} value={new_value}")

        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

        if changed_idx >= needed:
            return

        self._building = True
        try:
            force_total_weight(self.weight_spins, needed, changed_idx)
        finally:
            self._building = False

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
        log_info("ui", "button_click: reset_values")
        self._building = True
        for i in range(len(self.states)):
            self.states[i].value = 5.0
            self.slider_widgets[i].setValue(50)
            self.spin_widgets[i].setValue(5.0)
        self._building = False
        self.recompute()

    def recompute(self):
        selected, ratios = get_selected_profiles_and_ratios(
            self.profile_combos,
            self.weight_spins,
            self.mix_combo.currentText(),
            MIX_MODES,
        )
        rel = mixed_relevances(self.profiles, selected, ratios)

        vals = [s.value for s in self.states]
        score, used_rel, contrib = compute_score(vals, rel)

        score_for_tier = round(score, 3)
        tier = tier_from_score(score_for_tier, self.tier_thresholds)

        display_score = display_score_consistent(
            score,
            tier,
            self.tier_thresholds,
        )

        log_debug(
            "recompute",
            f"title='{self.title_edit.text().strip()}' selected={selected} ratios={ratios} "
            f"vals={vals} score={score:.4f} tier={tier} display={display_score:.2f}",
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

        t = self.ui_cfg.get("result_title", {})
        b = self.ui_cfg.get("result_body", {})

        font_pt = int(t.get("font_pt", 14))
        bold = bool(t.get("bold", True))
        title_color = str(t.get("color", "#444"))
        margin_bottom = int(t.get("margin_bottom_px", 6))
        gap_lines = int(t.get("gap_lines_after", 1))
        body_color = str(b.get("color", "#666"))

        title_css = (
            f"font-size: {font_pt}pt; "
            f"font-weight: {'700' if bold else '400'}; "
            f"color: {title_color}; "
            f"margin-bottom: {margin_bottom}px;"
        )
        body_css = f"color: {body_color};"
        gap_html = "<br>" * max(0, gap_lines)

        if title:
            safe_title = html.escape(title)
            self.summary_label.setText(
                f'<div style="{body_css}">'
                f'<div style="{title_css}">{safe_title}</div>'
                f"{gap_html}"
                f"Erősségek: {html.escape(top_str)}<br>"
                f"Gyengeség: {html.escape(low_str)}"
                f"</div>"
            )
        else:
            self.summary_label.setText(
                f'<div style="{body_css}">'
                f"Erősségek: {html.escape(top_str)}<br>"
                f"Gyengeség: {html.escape(low_str)}"
                f"</div>"
            )

        self.summary_label.setMinimumHeight(self.summary_label.sizeHint().height())
        self.summary_label.updateGeometry()
        self.result_card.layout().activate()
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
                QTableWidgetItem(f"{c:.2f}"),
            ]
            items[0].setToolTip(name)

            for cidx, it in enumerate(items):
                if cidx in (1, 2, 3):
                    it.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                else:
                    it.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.table.setItem(r, cidx, it)

    def _trim_pixmap(self, pm: QPixmap, pad: int = 12) -> QPixmap:
        img = pm.toImage().convertToFormat(pm.toImage().Format.Format_ARGB32)
        w, h = img.width(), img.height()

        bg = self.result_card.palette().window().color()
        br, bgc, bb = bg.red(), bg.green(), bg.blue()

        left, right = w, -1
        top, bottom = h, -1
        tol = 8

        for y in range(h):
            for x in range(w):
                c = img.pixelColor(x, y)
                if (
                    abs(c.red() - br) > tol
                    or abs(c.green() - bgc) > tol
                    or abs(c.blue() - bb) > tol
                ):
                    if x < left:
                        left = x
                    if x > right:
                        right = x
                    if y < top:
                        top = y
                    if y > bottom:
                        bottom = y

        if right < left or bottom < top:
            out = QPixmap(w + pad * 2, h + pad * 2)
            out.fill(bg)
            p = QPainter(out)
            p.drawPixmap(pad, pad, pm)
            p.end()
            return out

        cropped = pm.copy(left, top, (right - left + 1), (bottom - top + 1))

        out = QPixmap(cropped.width() + pad * 2, cropped.height() + pad * 2)
        out.fill(bg)
        p = QPainter(out)
        p.drawPixmap(pad, pad, cropped)
        p.end()
        return out

    def copy_to_clipboard(self):
        log_info("ui", "button_click: copy_to_clipboard")

        title = self.title_edit.text().strip() or "(nincs cím)"
        selected, ratios = get_selected_profiles_and_ratios(
            self.profile_combos,
            self.weight_spins,
            self.mix_combo.currentText(),
            MIX_MODES,
        )
        rel = mixed_relevances(self.profiles, selected, ratios)

        vals = [s.value for s in self.states]
        score, _, _ = compute_score(vals, rel)
        tier = tier_from_score(score, self.tier_thresholds)

        prof_part = " + ".join(
            [f"{p} ({int(round(r * 100))}%)" for p, r in zip(selected, ratios)]
        )

        lines = [f"{title} — {score:.1f}/10 (Tier {tier})", f"Profil: {prof_part}", ""]
        for s in self.states:
            lines.append(f"- {s.name}: {s.value:.1f}")

        text = "\n".join(lines)
        copy_text_to_clipboard(text)

        self.copy_btn.setText("✔ Részletes adatok másolva!")
        QTimer.singleShot(
            1500,
            lambda: self.copy_btn.setText("Részletes adatok másolása vágólapra"),
        )

    def copy_result_image_to_clipboard(self):
        copy_widget_as_pixmap(self.result_card)

        self.copy_img_btn.setText("✔ Másolva!")
        QTimer.singleShot(
            1500,
            lambda: self.copy_img_btn.setText("Eredmény másolása vágólapra"),
        )

def main():
    init_logger()
    log_info("app", "Starting AkihabaraiScore")

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "akihabarai_konyvespolc.score"
    )

    app = QApplication(sys.argv)

    icon = load_app_icon()
    app.setWindowIcon(icon)

    w = MainWindow()
    w.setWindowIcon(icon)
    w.resize(1200, 720)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()