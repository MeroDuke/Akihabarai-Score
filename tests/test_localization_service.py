import json

import app.services.localization_service as localization


def test_hungarian_is_default_and_fallback_language():
    assert localization.DEFAULT_LANGUAGE == "hu"
    assert localization.FALLBACK_LANGUAGE == "hu"
    assert localization.translate("app_mode.scored.label") == "Adatvezérelt"
    assert (
        localization.TranslationCatalog("test", {}).fallback_messages
        is localization.HUNGARIAN_MESSAGES
    )


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


def test_runtime_language_switch_logs_catalog_lookup_and_success():
    info_messages = []
    warning_messages = []
    service = localization.LocalizationService(
        "config/locales",
        log_info_func=lambda component, message: info_messages.append(
            (component, message)
        ),
        log_warning_func=lambda component, message: warning_messages.append(
            (component, message)
        ),
    )

    result = service.switch_language(
        "en",
        request_id="req-1",
        source="qt",
    )

    assert result.success is True
    assert result.active_language == "en"
    assert result.fallback is False
    assert service.translate("panel.input.title") == "Input"
    assert any(
        "language_change_received" in message
        and "request_id='req-1'" in message
        for _, message in info_messages
    )
    assert any(
        "catalog_lookup" in message
        and "en.json" in message
        and "exists=true" in message
        for _, message in info_messages
    )
    assert any(
        "catalog_load_completed" in message
        and "success=true" in message
        for _, message in info_messages
    )
    assert warning_messages == []


def test_runtime_missing_catalog_falls_back_to_hungarian(tmp_path):
    info_messages = []
    warning_messages = []
    service = localization.LocalizationService(
        tmp_path,
        log_info_func=lambda component, message: info_messages.append(
            (component, message)
        ),
        log_warning_func=lambda component, message: warning_messages.append(
            (component, message)
        ),
    )

    result = service.switch_language(
        "en",
        request_id="req-2",
        source="qt",
    )

    assert result.success is False
    assert result.active_language == "hu"
    assert result.fallback is True
    assert result.reason == "catalog_missing"
    assert any("catalog_load_failed" in message for _, message in warning_messages)
    assert any(
        "fallback=true" in message for _, message in info_messages
        if "language_change_completed" in message
    )


def test_missing_translation_key_is_logged_once_per_language():
    warning_messages = []
    service = localization.LocalizationService(
        "config/locales",
        log_info_func=lambda *_: None,
        log_warning_func=lambda component, message: warning_messages.append(
            (component, message)
        ),
    )
    service.switch_language("en", request_id="req-3", source="qt")

    service.translate("missing.test.key")
    service.translate("missing.test.key")

    fallback_messages = [
        message
        for _, message in warning_messages
        if "translation_key_fallback" in message
    ]
    assert len(fallback_messages) == 1


def test_repository_language_catalogs_have_matching_keys():
    hungarian = localization.load_translation_catalog("config/locales/hu.json")
    english = localization.load_translation_catalog(
        "config/locales/en.json",
        requested_language="en",
    )

    assert set(english.messages) == set(hungarian.messages)


def test_language_catalogs_use_the_same_offline_mode_icon():
    hungarian = localization.load_translation_catalog("config/locales/hu.json")
    english = localization.load_translation_catalog(
        "config/locales/en.json",
        requested_language="en",
    )

    assert hungarian.translate("title_mode.offline.button").startswith("✏ ")
    assert english.translate("title_mode.offline.button").startswith("✏ ")
