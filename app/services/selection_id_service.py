"""Helpers for keeping Qt selection labels separate from stable identifiers."""

from __future__ import annotations


IDENTIFIER_LABELS_PROPERTY = "identifierLabels"


def current_identifier(combo) -> str:
    current_data = getattr(combo, "currentData", None)
    data = current_data() if callable(current_data) else None
    if isinstance(data, str) and data:
        return data
    return combo.currentText()


def find_identifier(combo, identifier: str) -> int:
    find_data = getattr(combo, "findData", None)
    index = find_data(identifier) if callable(find_data) else -1
    if index >= 0:
        return index
    return combo.findText(identifier)


def set_identifier_labels(combo, labels: dict[str, str]) -> None:
    combo.setProperty(IDENTIFIER_LABELS_PROPERTY, dict(labels))


def identifier_labels(combo) -> dict[str, str]:
    labels = combo.property(IDENTIFIER_LABELS_PROPERTY)
    return labels if isinstance(labels, dict) else {}


def add_identifier_item(combo, identifier: str) -> None:
    label = identifier_labels(combo).get(identifier, identifier)
    combo.addItem(label, identifier)


def add_identifier_items(combo, identifiers) -> None:
    for identifier in identifiers:
        add_identifier_item(combo, identifier)
