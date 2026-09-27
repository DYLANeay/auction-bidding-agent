import pytest

from smaug.agent.connection.settings import read_connection_settings


def test_defaults_are_the_local_server(monkeypatch: pytest.MonkeyPatch) -> None:
    for variable in ["AH_HOST", "AH_PORT", "AH_TOKEN", "AH_NAME", "AH_PLAYER_ID"]:
        monkeypatch.delenv(variable, raising=False)
    settings = read_connection_settings([])
    assert settings.host == "localhost"
    assert settings.port == 8000
    assert settings.token == "play123"


def test_environment_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AH_HOST", "auction.example.org")
    monkeypatch.setenv("AH_PORT", "8022")
    settings = read_connection_settings([])
    assert settings.host == "auction.example.org"
    assert settings.port == 8022


def test_arguments_win_over_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AH_NAME", "FromEnv")
    settings = read_connection_settings(["--name", "FromArgs", "--player-id", "abc"])
    assert settings.name == "FromArgs"
    assert settings.player_id == "abc"


def test_bad_values_stop_before_connecting(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit):
        read_connection_settings(["--name", "x"])
    monkeypatch.setenv("AH_PORT", "not-a-port")
    with pytest.raises(SystemExit):
        read_connection_settings([])
