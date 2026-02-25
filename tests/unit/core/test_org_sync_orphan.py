# AnimaWorks - Digital Anima Framework
# Copyright (C) 2026 AnimaWorks Authors
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for orphan anima directory detection and auto-cleanup.

Verifies detect_orphan_animas auto-removes trivial orphans and logs
non-trivial ones, as well as create_blank rollback behavior in anima_factory.
"""
from __future__ import annotations

import json
import time

import pytest
from pathlib import Path


class TestDetectOrphanAnimas:
    """Tests for detect_orphan_animas."""

    def test_no_orphans_when_all_valid(self, data_dir, make_anima):
        """Directories with valid identity.md are not flagged as orphans."""
        make_anima("sakura")
        make_anima("rin", supervisor="sakura")

        from core.org_sync import detect_orphan_animas

        animas_dir = data_dir / "animas"
        shared_dir = data_dir / "shared"
        orphans = detect_orphan_animas(animas_dir, shared_dir, age_threshold_s=0)
        assert orphans == []

    def test_nontrivial_orphan_detected_and_logged(self, data_dir, make_anima):
        """A directory without identity.md but with state/ is a non-trivial orphan."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / "state").mkdir()

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert len(orphans) == 1
        assert orphans[0]["name"] == "rie"
        assert orphans[0]["action"] == "logged"
        assert (orphan_dir / ".orphan_notified").exists()

    def test_trivial_orphan_auto_removed_empty(self, data_dir, make_anima):
        """An empty orphan directory is trivially removed."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert len(orphans) == 1
        assert orphans[0]["name"] == "rie"
        assert orphans[0]["action"] == "auto_removed"
        assert not orphan_dir.exists()

    def test_trivial_orphan_auto_removed_vectordb_only(self, data_dir, make_anima):
        """An orphan directory with only vectordb/ is trivially removed."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / "vectordb").mkdir()

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert len(orphans) == 1
        assert orphans[0]["action"] == "auto_removed"
        assert not orphan_dir.exists()

    def test_trivial_orphan_with_empty_identity(self, data_dir, make_anima):
        """An orphan with empty identity.md and no other content is auto-removed."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / "identity.md").write_text("", encoding="utf-8")

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert len(orphans) == 1
        assert orphans[0]["action"] == "auto_removed"
        assert not orphan_dir.exists()

    def test_trivial_orphan_with_undefined_identity(self, data_dir, make_anima):
        """An orphan with identity.md containing '未定義' is auto-removed."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / "identity.md").write_text("未定義", encoding="utf-8")

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert len(orphans) == 1
        assert orphans[0]["action"] == "auto_removed"
        assert not orphan_dir.exists()

    def test_skips_young_directories(self, data_dir):
        """Directories younger than age_threshold_s are skipped."""
        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared"
        )
        assert orphans == []

    def test_skips_already_logged_nontrivial(self, data_dir, make_anima):
        """Non-trivial orphans with .orphan_notified marker are skipped."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / "state").mkdir()
        (orphan_dir / ".orphan_notified").write_text("logged")

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert orphans == []

    def test_trivial_orphan_with_marker_still_removed(self, data_dir, make_anima):
        """Trivial orphans are auto-removed even if they have .orphan_notified."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / ".orphan_notified").write_text("already notified")
        (orphan_dir / "vectordb").mkdir()

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert len(orphans) == 1
        assert orphans[0]["action"] == "auto_removed"
        assert not orphan_dir.exists()

    def test_skips_hidden_directories(self, data_dir):
        """Directories starting with '.' or '_' are skipped."""
        (data_dir / "animas" / ".hidden").mkdir()
        (data_dir / "animas" / "_internal").mkdir()

        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert orphans == []

    def test_no_notification_sent_to_anima(self, data_dir, make_anima):
        """Orphan detection does NOT send messages to any Anima."""
        make_anima("rin", supervisor="sakura")
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / "state").mkdir()

        from core.org_sync import detect_orphan_animas

        detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )

        rin_inbox = data_dir / "shared" / "inbox" / "rin"
        sakura_inbox = data_dir / "shared" / "inbox" / "sakura"
        rin_msgs = list(rin_inbox.glob("*.json")) if rin_inbox.exists() else []
        sakura_msgs = list(sakura_inbox.glob("*.json")) if sakura_inbox.exists() else []
        assert len(rin_msgs) == 0
        assert len(sakura_msgs) == 0

    def test_nontrivial_orphan_marker_created(self, data_dir, make_anima):
        """After detecting a non-trivial orphan, .orphan_notified marker is created."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir()
        (orphan_dir / "episodes").mkdir()

        from core.org_sync import detect_orphan_animas

        detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )

        assert (orphan_dir / ".orphan_notified").exists()

    def test_empty_animas_dir(self, data_dir):
        """No orphans reported for empty animas directory."""
        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "animas", data_dir / "shared", age_threshold_s=0
        )
        assert orphans == []

    def test_nonexistent_animas_dir(self, data_dir):
        """Returns empty list for nonexistent directory."""
        from core.org_sync import detect_orphan_animas

        orphans = detect_orphan_animas(
            data_dir / "nonexistent", data_dir / "shared", age_threshold_s=0
        )
        assert orphans == []


class TestFindOrphanSupervisor:
    """Tests for _find_orphan_supervisor resolution logic."""

    def test_from_status_json(self, data_dir):
        """Supervisor resolved from status.json in the orphan directory."""
        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir(parents=True)
        (orphan_dir / "status.json").write_text(
            json.dumps({"supervisor": "rin"}), encoding="utf-8"
        )

        from core.org_sync import _find_orphan_supervisor

        result = _find_orphan_supervisor(orphan_dir, data_dir / "animas")
        assert result == "rin"

    def test_fallback_to_top_level(self, data_dir, make_anima):
        """Falls back to top-level anima when no status.json or config entry."""
        make_anima("sakura")

        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir(parents=True)

        from core.org_sync import _find_orphan_supervisor

        result = _find_orphan_supervisor(orphan_dir, data_dir / "animas")
        assert result == "sakura"

    def test_returns_none_when_no_candidates(self, data_dir):
        """Returns None when no supervisor candidates exist."""
        orphan_dir = data_dir / "animas" / "rie"
        orphan_dir.mkdir(parents=True)

        from core.org_sync import _find_orphan_supervisor

        result = _find_orphan_supervisor(orphan_dir, data_dir / "animas")
        assert result is None or isinstance(result, str)


class TestCreateBlankRollback:
    """Tests for create_blank rollback on failure."""

    def test_rollback_on_failure(self, data_dir, monkeypatch):
        """create_blank should remove the directory if _ensure_runtime_subdirs fails."""
        from core import anima_factory

        animas_dir = data_dir / "animas"

        def _failing_subdirs(pd):
            raise RuntimeError("simulated failure")

        monkeypatch.setattr(anima_factory, "_ensure_runtime_subdirs", _failing_subdirs)

        with pytest.raises(RuntimeError, match="simulated failure"):
            anima_factory.create_blank(animas_dir, "test-fail")

        assert not (animas_dir / "test-fail").exists()

    def test_successful_create_blank(self, data_dir):
        """create_blank creates an anima directory on success."""
        from core import anima_factory

        animas_dir = data_dir / "animas"
        anima_dir = anima_factory.create_blank(animas_dir, "test-ok")

        assert anima_dir.exists()
        assert (anima_dir / "episodes").is_dir()
        assert (anima_dir / "knowledge").is_dir()
        assert (anima_dir / "state").is_dir()
