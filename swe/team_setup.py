#!/usr/bin/env python3
"""Create SWE-bench evaluation team (3 Animas) in the AnimaWorks runtime directory."""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = Path(__file__).parent / "configs" / "team.json"


def _ensure_init() -> None:
    """Run animaworks init if runtime dir doesn't exist."""
    home = Path.home() / ".animaworks"
    if not home.exists():
        logger.info("Running animaworks init --skip-anima ...")
        subprocess.run(
            [sys.executable, "-m", "main", "init", "--skip-anima"],
            check=True,
        )


def _register_credential(name: str, cfg: dict) -> None:
    """Register a credential in config.json if not already present."""
    config_path = Path.home() / ".animaworks" / "config.json"
    config = json.loads(config_path.read_text())
    creds = config.setdefault("credentials", {})
    if name not in creds:
        creds[name] = cfg
        config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        logger.info("Registered credential: %s", name)


def setup_team(config_path: Path = DEFAULT_CONFIG) -> list[str]:
    """Create agents defined in team config. Returns list of agent names."""
    _ensure_init()

    team_cfg = json.loads(config_path.read_text())
    agents = team_cfg["agents"]
    animas_dir = Path.home() / ".animaworks" / "animas"
    created = []

    for name, agent_cfg in agents.items():
        agent_dir = animas_dir / name
        if agent_dir.exists():
            logger.info("Agent %s already exists, updating config", name)
        else:
            agent_dir.mkdir(parents=True)
            logger.info("Created agent directory: %s", name)

        # status.json
        status = {
            "supervisor": agent_cfg.get("supervisor"),
            "role": agent_cfg.get("role", "general"),
            "enabled": True,
            "model": agent_cfg["model"],
            "max_turns": 100,
            "max_chains": 5,
        }
        if agent_cfg.get("credential"):
            status["credential"] = agent_cfg["credential"]
        (agent_dir / "status.json").write_text(
            json.dumps(status, indent=2, ensure_ascii=False)
        )

        # identity.md
        (agent_dir / "identity.md").write_text(
            f"# {name}\n\n{agent_cfg['identity']}\n"
        )

        # injection.md
        (agent_dir / "injection.md").write_text(agent_cfg["injection"] + "\n")

        # permissions.md — allow bash and file tools
        (agent_dir / "permissions.md").write_text(
            "## Allowed Commands\n- All commands allowed for SWE-bench evaluation\n"
        )

        # heartbeat.md — disable heartbeat
        (agent_dir / "heartbeat.md").write_text(
            "# Heartbeat\n\nHeartbeat disabled for SWE-bench evaluation.\n"
        )

        # Required subdirectories
        for subdir in [
            "state", "episodes", "knowledge", "procedures",
            "skills", "shortterm", "activity_log", "transcripts",
        ]:
            (agent_dir / subdir).mkdir(exist_ok=True)
        (agent_dir / "state" / "pending").mkdir(exist_ok=True)

        # Register in config.json
        config_path_runtime = Path.home() / ".animaworks" / "config.json"
        config = json.loads(config_path_runtime.read_text())
        animas_cfg = config.setdefault("animas", {})
        if name not in animas_cfg:
            animas_cfg[name] = {
                "supervisor": agent_cfg.get("supervisor"),
                "speciality": agent_cfg.get("role", "general"),
            }
            config_path_runtime.write_text(
                json.dumps(config, indent=2, ensure_ascii=False)
            )

        created.append(name)

    logger.info("Team setup complete: %s", created)
    return created


def teardown_team(config_path: Path = DEFAULT_CONFIG) -> None:
    """Remove agents created by setup_team."""
    team_cfg = json.loads(config_path.read_text())
    animas_dir = Path.home() / ".animaworks" / "animas"

    import shutil

    for name in team_cfg["agents"]:
        agent_dir = animas_dir / name
        if agent_dir.exists():
            shutil.rmtree(agent_dir)
            logger.info("Removed agent: %s", name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    import argparse

    p = argparse.ArgumentParser(description="SWE-bench team setup")
    p.add_argument("action", choices=["setup", "teardown"])
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = p.parse_args()

    if args.action == "setup":
        setup_team(args.config)
    else:
        teardown_team(args.config)
