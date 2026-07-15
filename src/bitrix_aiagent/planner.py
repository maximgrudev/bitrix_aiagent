from __future__ import annotations

import re
from dataclasses import dataclass

from .domain import Operation, OperationType


@dataclass(frozen=True)
class PlanResult:
    needs_clarification: bool
    clarification_questions: list[str]
    operations: list[Operation]
    summary: str


class PromptPlanner:
    """
    Deterministic parser used as an MVP replacement for an LLM planner.

    Supported text formats:
    1) "обнови инфоблок <iblock_id> элемент <element_id> поле <field>=<value>"
    2) "создай элемент в инфоблоке <iblock_id> имя=<name>"
    3) "удали элемент <element_id> из инфоблока <iblock_id>"
    4) "измени настройку <setting_key>=<value>"
    """

    _UPDATE_RE = re.compile(
        r"обнови\s+инфоблок\s+(?P<iblock>\d+)\s+элемент\s+(?P<element>\d+)\s+поле\s+(?P<field>[a-zA-Z0-9_]+)=(?P<value>.+)",
        flags=re.IGNORECASE,
    )
    _CREATE_RE = re.compile(
        r"создай\s+элемент\s+в\s+инфоблоке\s+(?P<iblock>\d+)\s+имя=(?P<name>.+)",
        flags=re.IGNORECASE,
    )
    _DELETE_RE = re.compile(
        r"удали\s+элемент\s+(?P<element>\d+)\s+из\s+инфоблока\s+(?P<iblock>\d+)",
        flags=re.IGNORECASE,
    )
    _SETTING_RE = re.compile(
        r"измени\s+настройку\s+(?P<key>[a-zA-Z0-9_.-]+)=(?P<value>.+)",
        flags=re.IGNORECASE,
    )

    def build_plan(self, raw_prompt: str, details: list[str]) -> PlanResult:
        merged = " ".join([raw_prompt.strip(), *[d.strip() for d in details if d.strip()]]).strip()
        if not merged:
            return PlanResult(
                needs_clarification=True,
                clarification_questions=["Опишите задачу: какой контент или настройку нужно изменить?"],
                operations=[],
                summary="",
            )

        lowered = merged.lower()
        if "код" in lowered or "php" in lowered or "js" in lowered:
            return PlanResult(
                needs_clarification=True,
                clarification_questions=[
                    "Я не изменяю код сайта. Уточните задачу в рамках контента (инфоблоки) или разрешенных настроек."
                ],
                operations=[],
                summary="",
            )

        operation = self._parse_operation(merged)
        if operation is None:
            return PlanResult(
                needs_clarification=True,
                clarification_questions=[
                    "Уточните формат команды. Пример: 'обнови инфоблок 12 элемент 44 поле TITLE=Новый заголовок'.",
                    "Для настройки: 'измени настройку seo.meta_title=Новый title'.",
                ],
                operations=[],
                summary="",
            )

        summary = self._summarize(operation)
        return PlanResult(
            needs_clarification=False,
            clarification_questions=[],
            operations=[operation],
            summary=summary,
        )

    def _parse_operation(self, text: str) -> Operation | None:
        update_match = self._UPDATE_RE.search(text)
        if update_match:
            return Operation.content(
                operation_type=OperationType.UPDATE_IBLOCK_ELEMENT,
                target={
                    "iblock_id": int(update_match.group("iblock")),
                    "element_id": int(update_match.group("element")),
                },
                payload={
                    "field": update_match.group("field"),
                    "value": update_match.group("value").strip(),
                },
            )

        create_match = self._CREATE_RE.search(text)
        if create_match:
            return Operation.content(
                operation_type=OperationType.CREATE_IBLOCK_ELEMENT,
                target={"iblock_id": int(create_match.group("iblock"))},
                payload={"name": create_match.group("name").strip()},
            )

        delete_match = self._DELETE_RE.search(text)
        if delete_match:
            return Operation.content(
                operation_type=OperationType.DELETE_IBLOCK_ELEMENT,
                target={
                    "iblock_id": int(delete_match.group("iblock")),
                    "element_id": int(delete_match.group("element")),
                },
                payload={},
            )

        setting_match = self._SETTING_RE.search(text)
        if setting_match:
            return Operation.setting(
                operation_type=OperationType.UPDATE_SITE_SETTING,
                target={"setting_key": setting_match.group("key")},
                payload={"value": setting_match.group("value").strip()},
            )

        return None

    def _summarize(self, operation: Operation) -> str:
        if operation.operation_type == OperationType.UPDATE_IBLOCK_ELEMENT:
            return (
                "Обновление элемента инфоблока "
                f"{operation.target['iblock_id']} (element={operation.target['element_id']}), "
                f"поле {operation.payload['field']} -> {operation.payload['value']}."
            )
        if operation.operation_type == OperationType.CREATE_IBLOCK_ELEMENT:
            return (
                "Создание элемента в инфоблоке "
                f"{operation.target['iblock_id']} с именем '{operation.payload['name']}'."
            )
        if operation.operation_type == OperationType.DELETE_IBLOCK_ELEMENT:
            return (
                "Удаление элемента "
                f"{operation.target['element_id']} из инфоблока {operation.target['iblock_id']}."
            )
        if operation.operation_type == OperationType.UPDATE_SITE_SETTING:
            return (
                "Изменение настройки "
                f"{operation.target['setting_key']} -> {operation.payload['value']}."
            )
        return "Неизвестная операция."

