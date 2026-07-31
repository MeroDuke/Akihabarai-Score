import json

from app.services.user_preferences_service import (
    JsonPreferenceStore,
    default_preferences_path,
)


def test_default_preferences_path_uses_platform_user_config_directory(tmp_path):
    assert default_preferences_path(
        environ={"APPDATA": str(tmp_path)},
        platform="win32",
        home=tmp_path,
    ) == tmp_path / "AkihabaraiScore" / "preferences.json"
    assert default_preferences_path(
        environ={"XDG_CONFIG_HOME": str(tmp_path)},
        platform="linux",
        home=tmp_path,
    ) == tmp_path / "akihabarai-score" / "preferences.json"


def test_language_preference_round_trip_preserves_unknown_fields(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text(
        json.dumps({"future": {"value": 42}}),
        encoding="utf-8",
    )
    messages = []
    store = JsonPreferenceStore(
        path,
        log_info_func=lambda component, message: messages.append(
            (component, message)
        ),
    )

    result = store.save_language("en", request_id="req-1")

    assert result.success is True
    assert store.load_language() == "en"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["ui"]["language"] == "en"
    assert payload["future"] == {"value": 42}
    assert any(
        "preference_save_completed" in message
        and "request_id='req-1'" in message
        and "success=true" in message
        for _, message in messages
    )


def test_missing_invalid_or_unknown_language_defaults_to_hungarian(tmp_path):
    path = tmp_path / "preferences.json"
    messages = []
    store = JsonPreferenceStore(
        path,
        log_info_func=lambda component, message: messages.append(message),
    )
    assert store.load_language() == "hu"

    path.write_text("{", encoding="utf-8")
    assert store.load_language() == "hu"

    path.write_text(
        json.dumps({"ui": {"language": "de"}}),
        encoding="utf-8",
    )
    assert store.load_language() == "hu"
    assert any("fallback=true" in message for message in messages)


def test_language_preference_load_logs_selected_language(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text(
        json.dumps({"ui": {"language": "en"}}),
        encoding="utf-8",
    )
    messages = []
    store = JsonPreferenceStore(
        path,
        log_info_func=lambda component, message: messages.append(message),
    )

    assert store.load_language() == "en"
    assert any(
        "value='en'" in message and "fallback=false" in message
        for message in messages
    )

def test_preference_write_failure_is_controlled(tmp_path):
    blocking_file = tmp_path / "not-a-directory"
    blocking_file.write_text("blocked", encoding="utf-8")
    store = JsonPreferenceStore(blocking_file / "preferences.json")

    result = store.save_language("en", request_id="req-2")

    assert result.success is False
    assert result.reason is not None
