from __future__ import annotations

from dataclasses import dataclass, field

from .domain import Operation, OperationType, SiteBinding


@dataclass
class BitrixExecutionResult:
    success: bool
    operation_type: OperationType
    message: str


@dataclass
class BitrixClient:
    """
    In-memory Bitrix API adapter for MVP/testing.

    In production this class should call Bitrix REST and use site-scoped tokens.
    """

    applied_operations: list[Operation] = field(default_factory=list)

    def execute(self, site: SiteBinding, operation: Operation) -> BitrixExecutionResult:
        # We intentionally restrict the API surface to content/settings operations.
        self.applied_operations.append(operation)
        if operation.operation_type == OperationType.UPDATE_IBLOCK_ELEMENT:
            return BitrixExecutionResult(
                success=True,
                operation_type=operation.operation_type,
                message=(
                    f"[{site.site_alias}] Обновлен элемент {operation.target['element_id']} "
                    f"в инфоблоке {operation.target['iblock_id']}."
                ),
            )
        if operation.operation_type == OperationType.CREATE_IBLOCK_ELEMENT:
            return BitrixExecutionResult(
                success=True,
                operation_type=operation.operation_type,
                message=f"[{site.site_alias}] Создан элемент в инфоблоке {operation.target['iblock_id']}.",
            )
        if operation.operation_type == OperationType.DELETE_IBLOCK_ELEMENT:
            return BitrixExecutionResult(
                success=True,
                operation_type=operation.operation_type,
                message=(
                    f"[{site.site_alias}] Удален элемент {operation.target['element_id']} "
                    f"из инфоблока {operation.target['iblock_id']}."
                ),
            )
        if operation.operation_type == OperationType.UPDATE_SITE_SETTING:
            return BitrixExecutionResult(
                success=True,
                operation_type=operation.operation_type,
                message=f"[{site.site_alias}] Изменена настройка {operation.target['setting_key']}.",
            )
        return BitrixExecutionResult(
            success=False,
            operation_type=operation.operation_type,
            message="Операция не поддерживается адаптером BitrixClient.",
        )

