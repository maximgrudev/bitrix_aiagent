from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class OperationScope(str, Enum):
    CONTENT = "content"
    SETTINGS = "settings"
    CODE = "code"


class SettingsAccessLevel(str, Enum):
    NONE = "none"
    LIMITED = "limited"
    FULL = "full"


class WorkflowState(str, Enum):
    DRAFT = "draft"
    NEED_CLARIFICATION = "need_clarification"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    EXECUTING = "executing"
    DONE = "done"
    FAILED = "failed"
    CANCELED = "canceled"


class OperationType(str, Enum):
    UPDATE_IBLOCK_ELEMENT = "update_iblock_element"
    CREATE_IBLOCK_ELEMENT = "create_iblock_element"
    DELETE_IBLOCK_ELEMENT = "delete_iblock_element"
    UPDATE_SITE_SETTING = "update_site_setting"
    TOUCH_CODE = "touch_code"  # reserved only for explicit deny checks


@dataclass(frozen=True)
class PermissionProfile:
    allowed_iblocks: set[int] = field(default_factory=set)
    settings_access: SettingsAccessLevel = SettingsAccessLevel.NONE
    allowed_setting_prefixes: tuple[str, ...] = tuple()


@dataclass(frozen=True)
class SiteBinding:
    tenant_id: str
    site_id: str
    site_alias: str
    bitrix_base_url: str
    api_token: str
    permission_profile: PermissionProfile


@dataclass(frozen=True)
class ChatBinding:
    tenant_id: str
    chat_id: str
    site_id: str
    default_site: bool = False


@dataclass(frozen=True)
class Operation:
    operation_type: OperationType
    scope: OperationScope
    target: dict[str, Any]
    payload: dict[str, Any]

    @staticmethod
    def content(
        operation_type: OperationType,
        target: dict[str, Any],
        payload: dict[str, Any],
    ) -> "Operation":
        return Operation(
            operation_type=operation_type,
            scope=OperationScope.CONTENT,
            target=target,
            payload=payload,
        )

    @staticmethod
    def setting(
        operation_type: OperationType,
        target: dict[str, Any],
        payload: dict[str, Any],
    ) -> "Operation":
        return Operation(
            operation_type=operation_type,
            scope=OperationScope.SETTINGS,
            target=target,
            payload=payload,
        )


@dataclass
class PendingCommand:
    command_id: str
    tenant_id: str
    chat_id: str
    site_id: str
    author_id: str
    original_prompt: str
    collected_details: list[str] = field(default_factory=list)
    state: WorkflowState = WorkflowState.DRAFT
    clarification_questions: list[str] = field(default_factory=list)
    proposed_operations: list[Operation] = field(default_factory=list)
    human_summary: str = ""
    failure_reason: str = ""

    @staticmethod
    def create(
        tenant_id: str,
        chat_id: str,
        site_id: str,
        author_id: str,
        original_prompt: str,
    ) -> "PendingCommand":
        return PendingCommand(
            command_id=str(uuid4()),
            tenant_id=tenant_id,
            chat_id=chat_id,
            site_id=site_id,
            author_id=author_id,
            original_prompt=original_prompt.strip(),
        )

