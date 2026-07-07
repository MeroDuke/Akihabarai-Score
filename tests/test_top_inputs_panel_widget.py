from app.core.constants import MIX_MODES
from app.widgets.top_inputs_panel_widget import TopInputsPanelWidget


def test_top_inputs_panel_uses_hungarian_labels_and_placeholder(qtbot):
    panel = TopInputsPanelWidget(
        title_placeholder="pl. Re:Zero S3",
        title_max_length=80,
        mix_mode_names=list(MIX_MODES.keys()),
        show_title_mode_button=True,
    )
    qtbot.addWidget(panel)

    assert panel.title_label.text() == "Anime / szezon cím:"
    assert panel.title_edit.placeholderText() == "pl. Re:Zero S3"
    assert panel.title_edit.maxLength() == 80
    assert panel.mix_label.text() == "Profil-mix mód:"
    assert panel.mix_combo.count() == len(MIX_MODES)
    assert not panel.title_mode_btn.isHidden()


def test_top_inputs_panel_can_hide_title_mode_button(qtbot):
    panel = TopInputsPanelWidget(
        title_placeholder="AniList keresés...",
        title_max_length=120,
        mix_mode_names=["Egy profil"],
        show_title_mode_button=False,
    )
    qtbot.addWidget(panel)

    assert panel.title_edit.placeholderText() == "AniList keresés..."
    assert panel.title_edit.maxLength() == 120
    assert panel.title_mode_btn.isHidden()
