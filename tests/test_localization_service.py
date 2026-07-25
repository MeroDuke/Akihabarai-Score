import json

import app.services.localization_service as localization


def test_hungarian_is_default_and_fallback_language():
    assert localization.DEFAULT_LANGUAGE == "hu"
    assert localization.FALLBACK_LANGUAGE == "hu"
    assert localization.translate("app_mode.scored.label") == "Adatvezérelt"


def test_missing_selected_language_key_falls_back_to_hungarian():
    translator = localization.build_translator(
        "en",
        {"app_mode.scored.label": "Data-driven"},
    )
    assert translator.translate("app_mode.scored.label") == "Data-driven"
    assert translator.translate("app_mode.freehand.label") == "Szabadkezes"
    assert translator.translate("unknown.key") == "unknown.key"


def test_translation_values_support_named_formatting_and_safe_missing_values():
    translator = localization.build_translator(
        "test",
        {"greeting": "Hello {name}", "broken": "Value {missing}"},
    )
    assert translator.translate("greeting", name="Akihabara") == "Hello Akihabara"
    assert translator.translate("broken") == "Value {missing}"


def test_catalog_loader_accepts_json_format(tmp_path):
    path = tmp_path / "en.json"
    path.write_text(
        json.dumps(
            {
                "language": "en",
                "messages": {"result.strengths": "Strengths"},
            }
        ),
        encoding="utf-8",
    )
    translator = localization.load_translation_catalog(path)
    assert translator.language == "en"
    assert translator.translate("result.strengths") == "Strengths"
    assert translator.translate("result.weakness") == "Gyengeség"


def test_invalid_or_missing_catalog_uses_hungarian_fallback(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    assert localization.load_translation_catalog(invalid).language == "hu"
    assert localization.load_translation_catalog(
        tmp_path / "missing.json"
    ).translate("dialog.yes") == "Igen"


def test_repository_hungarian_catalog_matches_builtin_keys():
    translator = localization.load_translation_catalog("config/locales/hu.json")
    assert translator.language == "hu"
    assert set(translator.messages) == set(localization.HUNGARIAN_MESSAGES)
