# AnimaWorks - Digital Person Framework
# Copyright (C) 2026 AnimaWorks Authors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of AnimaWorks core/server, licensed under AGPL-3.0.
# See LICENSES/AGPL-3.0.txt for the full license text.

"""AnimaWorks external tools package."""
from __future__ import annotations
import logging
import sys
from pathlib import Path

logger = logging.getLogger("animaworks.tools")

TOOL_MODULES = {
    "web_search": "core.tools.web_search",
    "x_search": "core.tools.x_search",
    "chatwork": "core.tools.chatwork",
    "slack": "core.tools.slack",
    "gmail": "core.tools.gmail",
    "local_llm": "core.tools.local_llm",
    "transcribe": "core.tools.transcribe",
    "aws_collector": "core.tools.aws_collector",
    "github": "core.tools.github",
    "image_gen": "core.tools.image_gen",
}


def discover_personal_tools(person_dir: Path) -> dict[str, str]:
    """Scan ``{person_dir}/tools/`` for personal tool modules.

    Returns:
        Mapping of tool_name → absolute file path.
        Skips files starting with ``_`` (including ``__init__.py``).
    """
    tools_dir = person_dir / "tools"
    if not tools_dir.is_dir():
        return {}
    personal: dict[str, str] = {}
    for f in sorted(tools_dir.glob("*.py")):
        if f.name.startswith("_"):
            continue
        tool_name = f.stem
        if tool_name in TOOL_MODULES:
            logger.warning(
                "Personal tool '%s' shadows core tool — skipped", tool_name,
            )
            continue
        personal[tool_name] = str(f)
    if personal:
        logger.info("Discovered personal tools: %s", list(personal.keys()))
    return personal


def cli_dispatch():
    """Entry point for ``animaworks-tool`` CLI command.

    Supports both core tools (from ``TOOL_MODULES``) and personal tools
    discovered via the ``ANIMAWORKS_PERSON_DIR`` environment variable.
    """
    import os

    # Discover personal tools if person_dir is set
    person_dir_str = os.environ.get("ANIMAWORKS_PERSON_DIR", "")
    personal: dict[str, str] = {}
    if person_dir_str:
        personal = discover_personal_tools(Path(person_dir_str))

    all_tools = set(TOOL_MODULES.keys()) | set(personal.keys())

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        tools = ", ".join(sorted(all_tools))
        print(f"Usage: animaworks-tool <tool_name> [args...]")
        print(f"Available tools: {tools}")
        sys.exit(0 if "--help" in sys.argv else 1)

    tool_name = sys.argv[1]

    # Try core tools first
    if tool_name in TOOL_MODULES:
        import importlib
        mod = importlib.import_module(TOOL_MODULES[tool_name])
        if not hasattr(mod, "cli_main"):
            print(f"Tool '{tool_name}' has no CLI interface")
            sys.exit(1)
        mod.cli_main(sys.argv[2:])
        return

    # Try personal tools
    if tool_name in personal:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            f"animaworks_personal_tool_{tool_name}", personal[tool_name],
        )
        if spec is None or spec.loader is None:
            print(f"Cannot load personal tool: {tool_name}")
            sys.exit(1)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        if not hasattr(mod, "cli_main"):
            print(f"Personal tool '{tool_name}' has no CLI interface")
            sys.exit(1)
        mod.cli_main(sys.argv[2:])
        return

    print(f"Unknown tool: {tool_name}")
    print(f"Available: {', '.join(sorted(all_tools))}")
    sys.exit(1)