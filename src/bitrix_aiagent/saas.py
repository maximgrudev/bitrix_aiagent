from __future__ import annotations

from dataclasses import dataclass, field

from .domain import ChatBinding, SiteBinding


class RegistryError(RuntimeError):
    pass


@dataclass
class MultiTenantRegistry:
    """Stores bindings for many sites across many Telegram chats."""

    sites: dict[str, SiteBinding] = field(default_factory=dict)
    chats: list[ChatBinding] = field(default_factory=list)

    def add_site(self, site: SiteBinding) -> None:
        self.sites[site.site_id] = site

    def bind_chat(self, binding: ChatBinding) -> None:
        self.chats.append(binding)

    def resolve_site_for_chat(self, tenant_id: str, chat_id: str) -> SiteBinding:
        candidates = [c for c in self.chats if c.tenant_id == tenant_id and c.chat_id == chat_id]
        if not candidates:
            raise RegistryError(f"Чат {chat_id} не привязан к сайтам в tenant {tenant_id}.")

        preferred = next((c for c in candidates if c.default_site), candidates[0])
        site = self.sites.get(preferred.site_id)
        if site is None:
            raise RegistryError(f"Сайт {preferred.site_id} не найден в реестре.")
        return site

