# AnimaWorks - Digital Anima Framework
# Copyright (C) 2026 AnimaWorks Authors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of AnimaWorks core/server, licensed under Apache-2.0.
# See LICENSE for the full license text.

"""i18n strings for meeting room manager."""

from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "room_manager.max_participants_exceeded": {
        "ja": "参加者は最大{max_n}人までです",
        "en": "Maximum {max_n} participants allowed",
    },
    "room_manager.chair_not_in_participants": {
        "ja": "議長は参加者に含まれている必要があります",
        "en": "Chair must be one of the participants",
    },
    "room_manager.room_not_found": {
        "ja": "会議室 '{room_id}' が見つかりません",
        "en": "Meeting room '{room_id}' not found",
    },
    "room_manager.room_closed": {
        "ja": "この会議室は閉鎖されています",
        "en": "This meeting room is closed",
    },
}
