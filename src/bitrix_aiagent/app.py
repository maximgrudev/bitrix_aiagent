from __future__ import annotations

from .admin_panel import SiteAccessPayload, SiteAdminPanelService
from .bitrix import BitrixClient
from .domain import SettingsAccessLevel
from .planner import PromptPlanner
from .policy import OperationPolicy
from .saas import MultiTenantRegistry
from .telegram import TelegramBotController, TelegramUpdate
from .workflow import CommandWorkflowService


def build_demo_controller() -> TelegramBotController:
    registry = MultiTenantRegistry()
    panel = SiteAdminPanelService(registry)
    panel.upsert_site_access(
        SiteAccessPayload(
            tenant_id="tenant-1",
            site_id="site-1",
            site_alias="shop-ru",
            bitrix_base_url="https://shop.example.com",
            api_token="token-1",
            allowed_iblocks={12, 18},
            settings_access=SettingsAccessLevel.LIMITED,
            allowed_setting_prefixes=("seo.", "ui."),
        )
    )
    panel.bind_chat_to_site(
        tenant_id="tenant-1",
        chat_id="chat-100",
        site_id="site-1",
        default_site=True,
    )
    workflow = CommandWorkflowService(
        planner=PromptPlanner(),
        policy=OperationPolicy(),
        bitrix_client=BitrixClient(),
    )
    return TelegramBotController(registry=registry, workflow=workflow)


def demo() -> None:
    bot = build_demo_controller()

    first = bot.handle_update(
        TelegramUpdate(
            tenant_id="tenant-1",
            chat_id="chat-100",
            user_id="u-1",
            text="обнови инфоблок 12 элемент 44 поле TITLE=Летняя коллекция",
        )
    )
    print(first.text)

    second = bot.handle_update(
        TelegramUpdate(
            tenant_id="tenant-1",
            chat_id="chat-100",
            user_id="u-1",
            text="confirm",
        )
    )
    print(second.text)


if __name__ == "__main__":
    demo()

