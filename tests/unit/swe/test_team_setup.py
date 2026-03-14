"""Tests for swe/team_setup.py."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from swe.team_setup import setup_team, teardown_team


@pytest.fixture
def tmp_animaworks(tmp_path):
    """Create a temporary AnimaWorks home directory."""
    home = tmp_path / ".animaworks"
    home.mkdir()
    animas = home / "animas"
    animas.mkdir()
    config = {
        "credentials": {"vllm-local": {"type": "api_key", "api_key": "dummy"}},
        "animas": {},
    }
    (home / "config.json").write_text(json.dumps(config))
    return home


@pytest.fixture
def team_config(tmp_path):
    """Create a minimal team config."""
    cfg = {
        "port": 18502,
        "timeout_minutes": 30,
        "agents": {
            "test-arch": {
                "model": "claude-sonnet-4-6",
                "role": "engineer",
                "supervisor": None,
                "credential": None,
                "identity": "Test architect",
                "injection": "## Role\nTest",
            },
            "test-inv": {
                "model": "openai/qwen3.5-35b-a3b",
                "role": "researcher",
                "supervisor": "test-arch",
                "credential": "vllm-local",
                "identity": "Test investigator",
                "injection": "## Role\nTest",
            },
        },
    }
    path = tmp_path / "team.json"
    path.write_text(json.dumps(cfg))
    return path


class TestSetupTeam:
    def test_creates_agent_directories(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                names = setup_team(team_config)

        assert set(names) == {"test-arch", "test-inv"}
        assert (tmp_animaworks / "animas" / "test-arch").is_dir()
        assert (tmp_animaworks / "animas" / "test-inv").is_dir()

    def test_creates_status_json(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)

        status = json.loads(
            (tmp_animaworks / "animas" / "test-arch" / "status.json").read_text()
        )
        assert status["model"] == "claude-sonnet-4-6"
        assert status["enabled"] is True
        assert status["supervisor"] is None

    def test_creates_identity_md(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)

        identity = (tmp_animaworks / "animas" / "test-arch" / "identity.md").read_text()
        assert "Test architect" in identity

    def test_creates_injection_md(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)

        injection = (tmp_animaworks / "animas" / "test-inv" / "injection.md").read_text()
        assert "## Role" in injection

    def test_creates_subdirectories(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)

        agent_dir = tmp_animaworks / "animas" / "test-arch"
        assert (agent_dir / "state").is_dir()
        assert (agent_dir / "state" / "pending").is_dir()
        assert (agent_dir / "episodes").is_dir()
        assert (agent_dir / "knowledge").is_dir()

    def test_sets_credential(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)

        status = json.loads(
            (tmp_animaworks / "animas" / "test-inv" / "status.json").read_text()
        )
        assert status["credential"] == "vllm-local"

    def test_registers_in_config(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)

        config = json.loads((tmp_animaworks / "config.json").read_text())
        assert "test-arch" in config["animas"]
        assert "test-inv" in config["animas"]

    def test_idempotent(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)
                names = setup_team(team_config)

        assert set(names) == {"test-arch", "test-inv"}


class TestTeardownTeam:
    def test_removes_agents(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            with patch("swe.team_setup._ensure_init"):
                setup_team(team_config)
                teardown_team(team_config)

        assert not (tmp_animaworks / "animas" / "test-arch").exists()
        assert not (tmp_animaworks / "animas" / "test-inv").exists()

    def test_noop_if_not_exists(self, tmp_animaworks, team_config):
        with patch("swe.team_setup.Path.home", return_value=tmp_animaworks.parent):
            teardown_team(team_config)
