from types import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QSizePolicy

from app.core.models import (
    ScoredDimension,
    ScoringInput,
    ScoringResult,
    ScoringSummary,
)
from app.widgets.result_panel_widget import (
    ResultPanelWidget,
)


def _result(states, *, display_score=8.3, tier="A"):
    dimensions = tuple(
        ScoredDimension(state.name, state.value)
        for state in states
    )
    return ScoringResult(
        score=display_score,
        display_score=display_score,
        tier=tier,
        input=ScoringInput(
            title="",
            selected_profiles=("Profile",),
            profile_ratios=(1.0,),
            dimensions=dimensions,
        ),
        relevances=tuple([1.0, 0.8][:len(states)]),
        contributions=tuple([4.5, 3.8][:len(states)]),
        summary=ScoringSummary(
            strengths=dimensions[:2],
            weakness=dimensions[-1],
        ),
    )


def test_result_panel_uses_hungarian_labels(qtbot):
    panel = ResultPanelWidget()
    qtbot.addWidget(panel)

    assert panel.title() == "Eredmény"
    assert panel.copy_img_btn.text() == "Eredmény képként másolása"
    assert [
        panel.table.horizontalHeaderItem(column).text()
        for column in range(panel.table.columnCount())
    ] == ["Dimenzió", "Pont", "Relevancia", "Hozzájárulás"]
    assert panel.copy_btn.text() == "Részletes adatok másolása vágólapra"


def test_result_panel_update_result_updates_labels_and_table(qtbot):
    panel = ResultPanelWidget()
    qtbot.addWidget(panel)

    states = [
        SimpleNamespace(name="Story", value=7.5),
        SimpleNamespace(name="Visuals", value=8.0),
    ]
    result = _result(states)

    panel.update_result(result, states, summary_html="<b>Summary</b>")

    assert panel.score_label.text() == "8.3 / 10"
    assert panel.tier_label.text() == "Tier: A"
    assert panel.summary_label.text() == "<b>Summary</b>"
    assert panel.table.rowCount() == 2
    assert panel.table.item(0, 0).text() == "Story"
    assert panel.table.item(0, 1).text() == "7.5"
    assert panel.table.item(0, 2).text() == "1.00"
    assert panel.table.item(0, 3).text() == "4.50"


def test_result_table_wraps_long_dimension_names_into_taller_rows(qtbot):
    panel = ResultPanelWidget()
    qtbot.addWidget(panel)
    panel.resize(500, 700)
    panel.show()

    states = [
        SimpleNamespace(name="Sound", value=5.0),
        SimpleNamespace(
            name=(
                "Direction and exceptionally long visual storytelling "
                "with additional layout-test wording"
            ),
            value=5.0,
        ),
    ]

    panel.update_result(_result(states), states, summary_html="")
    QApplication.processEvents()

    assert panel.table.wordWrap() is True
    assert panel.table.textElideMode() == Qt.TextElideMode.ElideNone
    assert panel.table.rowHeight(1) > panel.table.rowHeight(0)
    assert panel.table.item(1, 0).text() == states[1].name


def test_result_panel_keeps_result_summary_compact_and_table_scroll_free(qtbot):
    panel = ResultPanelWidget()
    qtbot.addWidget(panel)
    panel.resize(681, 1360)
    panel.show()

    states = [
        SimpleNamespace(name="T\u00f6rt\u00e9net / plot", value=5.0),
        SimpleNamespace(name="Karakterek", value=5.0),
        SimpleNamespace(name="Temp\u00f3 / epiz\u00f3dritmus", value=5.0),
        SimpleNamespace(name="Rendez\u00e9s & vizu\u00e1lis kompoz\u00edci\u00f3", value=5.0),
        SimpleNamespace(name="Anim\u00e1ci\u00f3 & koreogr\u00e1fia", value=5.0),
        SimpleNamespace(name="Vizu\u00e1lis diz\u00e1jn", value=5.0),
        SimpleNamespace(name="Hang", value=5.0),
        SimpleNamespace(name="Hat\u00e1s / \u00e9lm\u00e9ny", value=5.0),
    ]
    dimensions = tuple(
        ScoredDimension(state.name, state.value)
        for state in states
    )
    result = ScoringResult(
        score=5.0,
        display_score=5.0,
        tier="C",
        input=ScoringInput(
            title="",
            selected_profiles=("Profile",),
            profile_ratios=(1.0,),
            dimensions=dimensions,
        ),
        relevances=(0.9, 0.8, 0.6, 0.8, 0.7, 1.0, 0.7, 0.9),
        contributions=(4.5, 4.0, 3.0, 4.0, 3.5, 5.0, 3.5, 4.5),
        summary=ScoringSummary(
            strengths=dimensions[:2],
            weakness=dimensions[-1],
        ),
    )

    panel.update_result(
        result,
        states,
        summary_html=(
            "Er\u0151ss\u00e9gek: T\u00f6rt\u00e9net / plot (5),<br>"
            "Karakterek (5)<br>"
            "Gyenges\u00e9g: Hat\u00e1s / \u00e9lm\u00e9ny<br>"
            "(5)"
        ),
    )
    QApplication.processEvents()

    visible_rows_height = sum(
        panel.table.rowHeight(row)
        for row in range(panel.table.rowCount())
    )
    table_chrome_height = (
        panel.table.horizontalHeader().height()
        + panel.table.frameWidth() * 2
    )

    assert (
        panel.result_card.sizePolicy().verticalPolicy()
        == QSizePolicy.Policy.Fixed
    )
    assert panel.result_card.height() == panel.result_card.sizeHint().height()
    assert panel.table.minimumHeight() >= visible_rows_height + table_chrome_height
    assert not panel.table.verticalScrollBar().isVisible()


def test_result_panel_sanitize_summary_html_removes_inline_colors():
    html = '<div style="color: red; font-weight: 700"><font color="#fff">Text</font></div>'

    sanitized = ResultPanelWidget.sanitize_summary_html(html)

    assert "color: red" not in sanitized
    assert 'color="#fff"' not in sanitized
    assert "font-weight: 700" in sanitized
