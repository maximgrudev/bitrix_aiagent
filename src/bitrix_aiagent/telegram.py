from __future__ import annotations

from dataclasses import dataclass

from .saas import MultiTenantRegistry, RegistryError
from .workflow import BotReply, CommandWorkflowService
from .policy import PolicyViolationError


@dataclass(frozen=True)
class TelegramUpdate:
    tenant_id: str
    chat_id: str
    user_id: str
    text: str


class TelegramBotController:
    """
    Minimal controller for Telegram updates.

    Command contract:
    - "confirm" to run a prepared command
    - "cancel" to abort current command
    - any other text starts a command or adds clarification details
    """

    def __init__(self, registry: MultiTenantRegistry, workflow: CommandWorkflowService) -> None:
        self._registry = registry
        self._workflow = workflow

    def handle_update(self, update: TelegramUpdate) -> BotReply:
        text = update.text.strip()
        if not text:
            return BotReply(text="Пустое сообщение. Опишите задачу.", state=self._state_or_none(update))

        try:
            site = self._registry.resolve_site_for_chat(update.tenant_id, update.chat_id)
        except RegistryError as exc:
            return BotReply(text=f"Ошибка конфигурации чата: {exc}", state=self._state_or_none(update))

        command = text.lower()
        if command == "confirm":
            try:
                return self._workflow.confirm(site=site, chat_id=update.chat_id)
            except KeyError:
                return BotReply(text="Нет команды для подтверждения.", state=self._state_or_none(update))
        if command == "cancel":
            try:
                return self._workflow.cancel(chat_id=update.chat_id)
            except KeyError:
                return BotReply(text="Нет активной команды для отмены.", state=self._state_or_none(update))

        # If command is already active in this chat, treat text as details.
        try:
            return self._workflow.add_details(site=site, chat_id=update.chat_id, details=text)
        except KeyError:
            pass
        except PolicyViolationError as exc:
            return BotReply(text=f"Операция запрещена: {exc}", state=self._state_or_none(update))

        try:
            return self._workflow.start_command(
                site=site,
                chat_id=update.chat_id,
                author_id=update.user_id,
                prompt=text,
            )
        except PolicyViolationError as exc:
            return BotReply(text=f"Операция запрещена: {exc}", state=self._state_or_none(update))

    def _state_or_none(self, update: TelegramUpdate):
        # State-less default for transport-level responses.
        return None

