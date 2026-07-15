from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bitrix_aiagent.admin_panel import SiteAccessPayload, SiteAdminPanelService
from bitrix_aiagent.bitrix import BitrixClient
from bitrix_aiagent.domain import SettingsAccessLevel, WorkflowState
from bitrix_aiagent.planner import PromptPlanner
from bitrix_aiagent.policy import OperationPolicy
from bitrix_aiagent.saas import MultiTenantRegistry
from bitrix_aiagent.telegram import TelegramBotController, TelegramUpdate
from bitrix_aiagent.workflow import CommandWorkflowService


class WorkflowTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = MultiTenantRegistry()
        panel = SiteAdminPanelService(self.registry)
        panel.upsert_site_access(
            SiteAccessPayload(
                tenant_id="tenant-a",
                site_id="site-a",
                site_alias="main-site",
                bitrix_base_url="https://example.com",
                api_token="token",
                allowed_iblocks={10, 12},
                settings_access=SettingsAccessLevel.LIMITED,
                allowed_setting_prefixes=("seo.",),
            )
        )
        panel.bind_chat_to_site(
            tenant_id="tenant-a",
            chat_id="chat-1",
            site_id="site-a",
            default_site=True,
        )
        self.client = BitrixClient()
        self.workflow = CommandWorkflowService(
            planner=PromptPlanner(),
            policy=OperationPolicy(),
            bitrix_client=self.client,
        )
        self.bot = TelegramBotController(registry=self.registry, workflow=self.workflow)

    def test_happy_path_requires_confirmation(self) -> None:
        proposal = self.bot.handle_update(
            TelegramUpdate(
                tenant_id="tenant-a",
                chat_id="chat-1",
                user_id="u-1",
                text="обнови инфоблок 12 элемент 44 поле TITLE=Новый заголовок",
            )
        )
        self.assertEqual(proposal.state, WorkflowState.AWAITING_CONFIRMATION)
        self.assertIn("Подтвердите выполнение", proposal.text)
        self.assertEqual(len(self.client.applied_operations), 0)

        executed = self.bot.handle_update(
            TelegramUpdate(
                tenant_id="tenant-a",
                chat_id="chat-1",
                user_id="u-1",
                text="confirm",
            )
        )
        self.assertEqual(executed.state, WorkflowState.DONE)
        self.assertIn("Готово", executed.text)
        self.assertEqual(len(self.client.applied_operations), 1)

    def test_clarification_flow(self) -> None:
        question = self.bot.handle_update(
            TelegramUpdate(
                tenant_id="tenant-a",
                chat_id="chat-1",
                user_id="u-1",
                text="поменяй контент на главной",
            )
        )
        self.assertEqual(question.state, WorkflowState.NEED_CLARIFICATION)
        self.assertIn("Уточните формат команды", question.text)

        proposal = self.bot.handle_update(
            TelegramUpdate(
                tenant_id="tenant-a",
                chat_id="chat-1",
                user_id="u-1",
                text="обнови инфоблок 12 элемент 44 поле TITLE=Главная 2026",
            )
        )
        self.assertEqual(proposal.state, WorkflowState.AWAITING_CONFIRMATION)

    def test_reject_code_changes(self) -> None:
        answer = self.bot.handle_update(
            TelegramUpdate(
                tenant_id="tenant-a",
                chat_id="chat-1",
                user_id="u-1",
                text="измени php код шаблона",
            )
        )
        self.assertEqual(answer.state, WorkflowState.NEED_CLARIFICATION)
        self.assertIn("не изменяю код сайта", answer.text.lower())

    def test_settings_are_limited_by_prefix(self) -> None:
        denied = self.bot.handle_update(
            TelegramUpdate(
                tenant_id="tenant-a",
                chat_id="chat-1",
                user_id="u-1",
                text="измени настройку cache.ttl=120",
            )
        )
        self.assertEqual(denied.state, WorkflowState.FAILED)
        self.assertIn("Операция запрещена", denied.text)

        allowed = self.bot.handle_update(
            TelegramUpdate(
                tenant_id="tenant-a",
                chat_id="chat-1",
                user_id="u-1",
                text="измени настройку seo.meta_title=Лето",
            )
        )
        self.assertEqual(allowed.state, WorkflowState.AWAITING_CONFIRMATION)


if __name__ == "__main__":
    unittest.main()

