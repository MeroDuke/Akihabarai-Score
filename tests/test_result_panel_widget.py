from types import SimpleNamespace

from PyQt6.QtWidgets import QApplication, QSizePolicy

from app.widgets.result_panel_widget import (
    ResultPanelWidget,
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
    result = {
        "display_score": 8.3,
        "tier": "A",
        "summary_html": "<b>Summary</b>",
        "relevances": [1.0, 0.8],
        "contributions": [4.5, 3.8],
    }

    panel.update_result(result, states)

    assert panel.score_label.text() == "8.3 / 10"
    assert panel.tier_label.text() == "Tier: A"
    assert panel.summary_label.text() == "<b>Summary</b>"
    assert panel.table.rowCount() == 2
    assert panel.table.item(0, 0).text() == "Story"
    assert panel.table.item(0, 1).text() == "7.5"
    assert panel.table.item(0, 2).text() == "1.00"
    assert panel.table.item(0, 3).text() == "4.50"


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
    result = {
        "display_score": 5.0,
        "tier": "C",
        "summary_html": (
            "Er\u0151ss\u00e9gek: T\u00f6rt\u00e9net / plot (5),<br>"
            "Karakterek (5)<br>"
            "Gyenges\u00e9g: Hat\u00e1s / \u00e9lm\u00e9ny<br>"
            "(5)"
        ),
        "relevances": [0.9, 0.8, 0.6, 0.8, 0.7, 1.0, 0.7, 0.9],
        "contributions": [4.5, 4.0, 3.0, 4.0, 3.5, 5.0, 3.5, 4.5],
    }

    panel.update_result(result, states)
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
