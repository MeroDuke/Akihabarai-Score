from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget

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


def test_result_table_uses_uniform_two_line_row_heights(qtbot):
    panel = ResultPanelWidget()
    qtbot.addWidget(panel)
    panel.resize(341, 720)
    panel.show()

    states = [
        SimpleNamespace(name="Sound", value=5.0),
        SimpleNamespace(name="Rendezés & vizuális történetmesélés", value=5.0),
    ]

    panel.update_result(_result(states), states, summary_html="")
    QApplication.processEvents()

    assert panel.table.wordWrap() is True
    assert panel.table.textElideMode() == Qt.TextElideMode.ElideNone
    expected_height = max(
        panel.table.verticalHeader().defaultSectionSize(),
        panel.table.fontMetrics().lineSpacing() * 2
        + panel.TABLE_ROW_VERTICAL_PADDING,
    )
    assert panel.table.rowHeight(0) == expected_height
    assert panel.table.rowHeight(1) == expected_height
    assert panel.table.item(1, 0).text() == states[1].name


@pytest.mark.parametrize("point_size", [10, 14, 18])
def test_compact_rows_save_space_without_shrinking_text(qtbot, point_size):
    panel = ResultPanelWidget()
    qtbot.addWidget(panel)
    font = panel.table.font()
    font.setPointSize(point_size)
    panel.table.setFont(font)
    states = [SimpleNamespace(name="Rendezés & vizuális történetmesélés", value=5)] * 8
    panel.update_table(states, [1.0] * 8, [5.0] * 8)
    line_height = panel.table.fontMetrics().lineSpacing()
    default_height = panel.table.verticalHeader().defaultSectionSize()
    former_height = max(default_height, 2 * line_height + 4)
    actual_height = panel.table.rowHeight(0)
    assert panel.table.font().pointSize() == point_size
    assert actual_height >= 2 * line_height + 2
    assert actual_height <= former_height
    assert former_height - actual_height <= 2
    assert len({panel.table.rowHeight(row) for row in range(8)}) == 1


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
    assert panel.table.height() >= visible_rows_height + table_chrome_height
    assert not panel.table.verticalScrollBar().isVisible()
    assert panel.table.viewport().height() == visible_rows_height
    assert (
        panel.table.geometry().top() - panel.copy_img_btn.geometry().bottom() - 1
        == panel.layout().spacing()
    )
    assert (
        panel.copy_btn.geometry().top() - panel.table.geometry().bottom() - 1
        == panel.layout().spacing()
    )


@pytest.mark.parametrize("point_size", [10, 14, 18])
def test_result_table_yields_space_to_copy_button_in_constrained_panel(qtbot, point_size):
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    panel = ResultPanelWidget()
    font = panel.table.font()
    font.setPointSize(point_size)
    panel.table.setFont(font)
    layout.addWidget(panel)
    host.setFixedSize(420, 500)
    summary_states = [SimpleNamespace(name="Story", value=7.9)]
    panel.update_result(
        _result(summary_states), summary_states,
        summary_html="Legmagasabb pontszámok:<br>Történet / plot (7.9)<br>Legalacsonyabb pontszám: Hang (5)",
    )
    states = [SimpleNamespace(name="Rendezés & vizuális történetmesélés", value=7.9)] * 8
    panel.update_table(states, [0.7] * 8, [5.53] * 8)
    host.show()
    QApplication.processEvents()

    assert panel.table.geometry().bottom() < panel.copy_btn.geometry().top()
    assert panel.copy_btn.geometry().bottom() < panel.height()
    assert panel.table.verticalScrollBar().maximum() > 0
    panel.table.scrollToBottom()
    QApplication.processEvents()
    last_cell = panel.table.visualItemRect(panel.table.item(7, 0))
    assert last_cell.top() >= 0
    assert last_cell.bottom() < panel.table.viewport().height()
    assert panel.result_card.height() == panel.result_card.sizeHint().height()


def test_compact_spacing_keeps_all_rows_visible_near_height_limit(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    outer = QVBoxLayout(host)
    panel = ResultPanelWidget()
    outer.addWidget(panel)
    states = [SimpleNamespace(name="Sound", value=5.0)] * 8
    panel.update_table(states, [1.0] * 8, [5.0] * 8)
    panel._sync_result_card_height()
    host.resize(500, 900)
    host.show()
    qtbot.wait(50)

    # Fit the table exactly, then compare the former 10px gaps at the same size.
    chrome = panel.table.height() - panel.table.viewport().height()
    rows = sum(panel.table.rowHeight(row) for row in range(8))
    surplus = (
        panel.table.height() - chrome - rows
        + panel.layout().itemAt(1).geometry().height()
    )
    host.setFixedSize(host.width(), host.height() - surplus + 2)
    qtbot.wait(50)
    assert not panel.table.verticalScrollBar().isVisible()

    panel.layout().setSpacing(10)
    panel.result_card.layout().setSpacing(10)
    panel._sync_result_card_height()
    qtbot.waitUntil(panel.table.verticalScrollBar().isVisible)
    assert panel.table.geometry().bottom() < panel.copy_btn.geometry().top()


def test_result_panel_sanitize_summary_html_removes_inline_colors():
    html = '<div style="color: red; font-weight: 700"><font color="#fff">Text</font></div>'

    sanitized = ResultPanelWidget.sanitize_summary_html(html)

    assert "color: red" not in sanitized
    assert 'color="#fff"' not in sanitized
    assert "font-weight: 700" in sanitized
