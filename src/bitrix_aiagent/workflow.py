from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .bitrix import BitrixClient
from .domain import PendingCommand, SiteBinding, WorkflowState
from .planner import PlanResult, PromptPlanner
from .policy import OperationPolicy, PolicyViolationError


@dataclass(frozen=True)
class BotReply:
    text: str
    state: Optional[WorkflowState]


class CommandWorkflowService:
    def __init__(
        self,
        planner: PromptPlanner,
        policy: OperationPolicy,
        bitrix_client: BitrixClient,
    ) -> None:
        self._planner = planner
        self._policy = policy
        self._bitrix_client = bitrix_client
        self._pending_by_chat: dict[str, PendingCommand] = {}

    def start_command(
        self,
        site: SiteBinding,
        chat_id: str,
        author_id: str,
        prompt: str,
    ) -> BotReply:
        command = PendingCommand.create(
            tenant_id=site.tenant_id,
            chat_id=chat_id,
            site_id=site.site_id,
            author_id=author_id,
            original_prompt=prompt,
        )
        self._pending_by_chat[chat_id] = command
        try:
            return self._advance_to_plan(site=site, command=command)
        except PolicyViolationError:
            command.state = WorkflowState.FAILED
            self._pending_by_chat.pop(chat_id, None)
            raise

    def add_details(self, site: SiteBinding, chat_id: str, details: str) -> BotReply:
        command = self._require_pending(chat_id)
        if command.state not in {WorkflowState.NEED_CLARIFICATION, WorkflowState.DRAFT}:
            return BotReply(
                text="Уточнения уже не нужны. Подтвердите 'confirm' или отмените 'cancel'.",
                state=command.state,
            )

        command.collected_details.append(details.strip())
        try:
            return self._advance_to_plan(site=site, command=command)
        except PolicyViolationError:
            command.state = WorkflowState.FAILED
            self._pending_by_chat.pop(chat_id, None)
            raise

    def confirm(self, site: SiteBinding, chat_id: str) -> BotReply:
        command = self._require_pending(chat_id)
        if command.state != WorkflowState.AWAITING_CONFIRMATION:
            return BotReply(
                text="Нет команды, ожидающей подтверждение.",
                state=command.state,
            )

        command.state = WorkflowState.EXECUTING
        try:
            messages: list[str] = []
            for operation in command.proposed_operations:
                self._policy.assert_allowed(operation, site.permission_profile)
                result = self._bitrix_client.execute(site, operation)
                if not result.success:
                    raise RuntimeError(result.message)
                messages.append(result.message)
            command.state = WorkflowState.DONE
            self._pending_by_chat.pop(chat_id, None)
            return BotReply(
                text="Готово:\n" + "\n".join(messages),
                state=WorkflowState.DONE,
            )
        except (PolicyViolationError, RuntimeError) as exc:
            command.state = WorkflowState.FAILED
            command.failure_reason = str(exc)
            return BotReply(
                text=f"Не удалось выполнить команду: {exc}",
                state=WorkflowState.FAILED,
            )

    def cancel(self, chat_id: str) -> BotReply:
        command = self._require_pending(chat_id)
        command.state = WorkflowState.CANCELED
        self._pending_by_chat.pop(chat_id, None)
        return BotReply(text="Команда отменена.", state=WorkflowState.CANCELED)

    def _advance_to_plan(self, site: SiteBinding, command: PendingCommand) -> BotReply:
        plan: PlanResult = self._planner.build_plan(
            raw_prompt=command.original_prompt,
            details=command.collected_details,
        )
        if plan.needs_clarification:
            command.state = WorkflowState.NEED_CLARIFICATION
            command.clarification_questions = plan.clarification_questions
            return BotReply(
                text="\n".join(plan.clarification_questions),
                state=WorkflowState.NEED_CLARIFICATION,
            )

        for operation in plan.operations:
            self._policy.assert_allowed(operation, site.permission_profile)

        command.proposed_operations = plan.operations
        command.human_summary = plan.summary
        command.state = WorkflowState.AWAITING_CONFIRMATION
        return BotReply(
            text=(
                "План операции:\n"
                f"{plan.summary}\n\n"
                "Подтвердите выполнение командой 'confirm' или отмените 'cancel'."
            ),
            state=WorkflowState.AWAITING_CONFIRMATION,
        )

    def _require_pending(self, chat_id: str) -> PendingCommand:
        command = self._pending_by_chat.get(chat_id)
        if command is None:
            raise KeyError(f"Нет активной команды для чата {chat_id}.")
        return command

