from __future__ import annotations

from dataclasses import dataclass

from .domain import Operation, OperationScope, OperationType, PermissionProfile, SettingsAccessLevel


class PolicyViolationError(RuntimeError):
    """Raised when an operation is not allowed by policy."""


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str = ""


class OperationPolicy:
    """Enforces allow-list access to Bitrix operations."""

    def evaluate(self, operation: Operation, profile: PermissionProfile) -> PolicyDecision:
        if operation.scope == OperationScope.CODE or operation.operation_type == OperationType.TOUCH_CODE:
            return PolicyDecision(
                allowed=False,
                reason="Изменение кода сайта запрещено политикой безопасности.",
            )

        if operation.scope == OperationScope.CONTENT:
            return self._evaluate_content(operation, profile)

        if operation.scope == OperationScope.SETTINGS:
            return self._evaluate_setting(operation, profile)

        return PolicyDecision(allowed=False, reason="Неизвестная область операции.")

    def assert_allowed(self, operation: Operation, profile: PermissionProfile) -> None:
        decision = self.evaluate(operation, profile)
        if not decision.allowed:
            raise PolicyViolationError(decision.reason)

    def _evaluate_content(self, operation: Operation, profile: PermissionProfile) -> PolicyDecision:
        iblock_id = operation.target.get("iblock_id")
        if not isinstance(iblock_id, int):
            return PolicyDecision(allowed=False, reason="Не указан корректный iblock_id.")
        if iblock_id not in profile.allowed_iblocks:
            return PolicyDecision(
                allowed=False,
                reason=f"Нет прав на инфоблок {iblock_id}.",
            )
        return PolicyDecision(allowed=True)

    def _evaluate_setting(self, operation: Operation, profile: PermissionProfile) -> PolicyDecision:
        if profile.settings_access == SettingsAccessLevel.NONE:
            return PolicyDecision(
                allowed=False,
                reason="Редактирование настроек отключено для сайта.",
            )

        key = operation.target.get("setting_key")
        if not isinstance(key, str):
            return PolicyDecision(allowed=False, reason="Не указан ключ настройки.")

        if profile.settings_access == SettingsAccessLevel.FULL:
            return PolicyDecision(allowed=True)

        if profile.settings_access == SettingsAccessLevel.LIMITED:
            if any(key.startswith(prefix) for prefix in profile.allowed_setting_prefixes):
                return PolicyDecision(allowed=True)
            return PolicyDecision(
                allowed=False,
                reason=f"Настройка {key} не входит в разрешенные области.",
            )

        return PolicyDecision(allowed=False, reason="Неподдерживаемый уровень доступа.")

