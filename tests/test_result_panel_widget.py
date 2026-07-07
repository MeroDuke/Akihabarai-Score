from types import SimpleNamespace

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


def test_result_panel_sanitize_summary_html_removes_inline_colors():
    html = '<div style="color: red; font-weight: 700"><font color="#fff">Text</font></div>'

    sanitized = ResultPanelWidget.sanitize_summary_html(html)

    assert "color: red" not in sanitized
    assert 'color="#fff"' not in sanitized
    assert "font-weight: 700" in sanitized
