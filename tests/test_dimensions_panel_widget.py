from app.core.models import DimState
from app.widgets.dimensions_panel_widget import DimensionsPanelWidget


def test_dimensions_panel_uses_hungarian_labels(qtbot):
    panel = DimensionsPanelWidget([DimState("Történet / plot")])
    qtbot.addWidget(panel)

    assert panel.title() == "Dimenziók"
    assert panel.header_name.text() == "Dimenzió"
    assert panel.header_value.text() == "Pont (1-10)"
    assert panel.dimension_labels[0].text() == "Történet / plot"


def test_dimensions_panel_builds_controls_for_each_state(qtbot):
    states = [
        DimState("Történet / plot", 7.5),
        DimState("Karakterek", 4.2),
    ]

    panel = DimensionsPanelWidget(states)
    qtbot.addWidget(panel)

    assert len(panel.dimension_labels) == 2
    assert len(panel.slider_widgets) == 2
    assert len(panel.spin_widgets) == 2

    assert panel.slider_widgets[0].minimum() == 10
    assert panel.slider_widgets[0].maximum() == 100
    assert panel.slider_widgets[0].value() == 75

    assert panel.spin_widgets[0].minimum() == 1.0
    assert panel.spin_widgets[0].maximum() == 10.0
    assert panel.spin_widgets[0].singleStep() == 0.1
    assert panel.spin_widgets[0].decimals() == 1
    assert panel.spin_widgets[0].value() == 7.5

    assert panel.slider_widgets[1].value() == 42
    assert panel.spin_widgets[1].value() == 4.2
