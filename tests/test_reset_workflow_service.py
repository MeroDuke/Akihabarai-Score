from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QLineEdit, QSlider, QSpinBox

from app.core.models import DimState
from app.services.reset_workflow_service import reset_score_inputs_to_initial_state


class FakeTitleSearchController:
    def __init__(self):
        self.reset_calls = 0

    def reset_online_state(self):
        self.reset_calls += 1


def test_reset_score_inputs_to_initial_state_resets_controls_and_returns_state(qtbot):
    title_edit = QLineEdit()
    title_edit.setText("Cowboy Bebop")
    qtbot.addWidget(title_edit)

    controller = FakeTitleSearchController()

    mix_combo = QComboBox()
    mix_combo.addItems(["1 profil", "2 profil"])
    mix_combo.setCurrentIndex(1)
    qtbot.addWidget(mix_combo)

    states = [DimState("Story", 8.0), DimState("Characters", 7.0)]
    sliders = [QSlider(), QSlider()]
    spins = [QDoubleSpinBox(), QDoubleSpinBox()]
    for slider in sliders:
        slider.setValue(80)
        qtbot.addWidget(slider)
    for spin in spins:
        spin.setValue(8.0)
        qtbot.addWidget(spin)

    profile_combos = [QComboBox(), QComboBox()]
    for combo in profile_combos:
        combo.addItems(["Balanced", "Drama"])
        combo.setCurrentIndex(1)
        qtbot.addWidget(combo)

    weight_spins = [QSpinBox(), QSpinBox()]
    for spin in weight_spins:
        spin.setRange(0, 100)
        spin.setValue(50)
        qtbot.addWidget(spin)

    building_values = []
    update_calls = []

    reset_state = reset_score_inputs_to_initial_state(
        set_building=lambda value: building_values.append(value),
        title_edit=title_edit,
        title_search_controller=controller,
        mix_combo=mix_combo,
        states=states,
        slider_widgets=sliders,
        spin_widgets=spins,
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        profile_names=["Balanced", "Drama"],
        total_weight=100,
        update_profile_combo_options=lambda: update_calls.append(True),
    )

    assert building_values == [True, False]
    assert title_edit.text() == ""
    assert controller.reset_calls == 1
    assert mix_combo.currentIndex() == 0
    assert [state.value for state in states] == [5.0, 5.0]
    assert [slider.value() for slider in sliders] == [50, 50]
    assert [spin.value() for spin in spins] == [5.0, 5.0]
    assert [combo.currentIndex() for combo in profile_combos] == [0, 0]
    assert [spin.value() for spin in weight_spins] == [100, 0]
    assert update_calls == [True]
    assert reset_state.selected_anime_result is None
    assert reset_state.selected_cover_pixmap is None
    assert reset_state.profile_selection_memory == ["Balanced", "Drama", "Balanced"]
    assert reset_state.current_mix_needed == 1


def test_reset_score_inputs_to_initial_state_clears_building_on_error(qtbot):
    title_edit = QLineEdit()
    qtbot.addWidget(title_edit)
    mix_combo = QComboBox()
    mix_combo.addItem("1 profil")
    qtbot.addWidget(mix_combo)

    building_values = []

    try:
        reset_score_inputs_to_initial_state(
            set_building=lambda value: building_values.append(value),
            title_edit=title_edit,
            title_search_controller=None,
            mix_combo=mix_combo,
            states=[],
            slider_widgets=[],
            spin_widgets=[],
            profile_combos=[],
            weight_spins=[],
            profile_names=[],
            total_weight=100,
            update_profile_combo_options=lambda: (_ for _ in ()).throw(
                RuntimeError("boom")
            ),
        )
    except RuntimeError as exc:
        error = exc
    else:
        error = None

    assert isinstance(error, RuntimeError)
    assert str(error) == "boom"
    assert building_values == [True, False]
