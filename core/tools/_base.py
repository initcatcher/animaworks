# AnimaWorks - Digital Person Framework
# Copyright (C) 2026 AnimaWorks Authors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of AnimaWorks core/server, licensed under AGPL-3.0.
# See LICENSES/AGPL-3.0.txt for the full license text.

"""Base infrastructure for AnimaWorks tools."""
from __future__ import annotations
import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("animaworks.tools")


class ToolConfigError(Exception):
    """Raised when a tool's configuration is incomplete."""
    pass


@dataclass
class ToolResult:
    """Standardized return value from tool execution."""
    success: bool
    data: Any = None
    text: str = ""
    error: str | None = None


def get_env_or_fail(key: str, tool_name: str) -> str:
    """Get an environment variable, raising a clear error if missing."""
    val = os.environ.get(key)
    if not val:
        raise ToolConfigError(
            f"Tool '{tool_name}' requires environment variable {key}. "
            f"Set it in .env or the shell environment."
        )
    return val


# ── CLI Guide Auto-Generation ────────────────────────────────


def auto_cli_guide(tool_name: str, schemas: list[dict[str, Any]]) -> str:
    """Auto-generate a CLI usage guide from tool schemas.

    Produces a markdown snippet showing ``animaworks-tool`` CLI usage for
    each schema, deriving argument flags from JSON Schema properties.

    Args:
        tool_name: The TOOL_MODULES key (e.g. ``"web_search"``).
        schemas: The list returned by ``get_tool_schemas()``.

    Returns:
        Markdown string with CLI examples.
    """
    lines = [f"### {tool_name}", "```bash"]
    for schema in schemas:
        params = schema.get("input_schema", schema.get("parameters", {}))
        props = params.get("properties", {})
        required = set(params.get("required", []))

        parts = [f"animaworks-tool {tool_name}"]
        # Positional: first required string parameter
        for pname in required:
            prop = props.get(pname, {})
            if prop.get("type") == "string":
                parts.append(f'"<{pname}>"')
                break
        # Optional flags
        for pname, prop in props.items():
            if pname in required:
                continue
            flag = f"--{pname.replace('_', '-')}"
            ptype = prop.get("type", "string")
            if ptype == "boolean":
                parts.append(f"[{flag}]")
            else:
                parts.append(f"[{flag} <{ptype}>]")
        parts.append("-j")
        lines.append(" ".join(parts))
    lines.append("```")
    return "\n".join(lines)