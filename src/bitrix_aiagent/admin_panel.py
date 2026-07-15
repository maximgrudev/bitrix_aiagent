from __future__ import annotations

from dataclasses import dataclass

from .domain import ChatBinding, PermissionProfile, SettingsAccessLevel, SiteBinding
from .saas import MultiTenantRegistry


@dataclass(frozen=True)
class SiteAccessPayload:
    tenant_id: str
    site_id: str
    site_alias: str
    bitrix_base_url: str
    api_token: str
    allowed_iblocks: set[int]
    settings_access: SettingsAccessLevel
    allowed_setting_prefixes: tuple[str, ...]


class SiteAdminPanelService:
    """
    Service layer for issuing per-site access and chat bindings.

    This mimics what a Bitrix admin panel module would call.
    """

    def __init__(self, registry: MultiTenantRegistry) -> None:
        self._registry = registry

    def upsert_site_access(self, payload: SiteAccessPayload) -> SiteBinding:
        profile = PermissionProfile(
            allowed_iblocks=payload.allowed_iblocks,
            settings_access=payload.settings_access,
            allowed_setting_prefixes=payload.allowed_setting_prefixes,
        )
        site = SiteBinding(
            tenant_id=payload.tenant_id,
            site_id=payload.site_id,
            site_alias=payload.site_alias,
            bitrix_base_url=payload.bitrix_base_url,
            api_token=payload.api_token,
            permission_profile=profile,
        )
        self._registry.add_site(site)
        return site

    def bind_chat_to_site(
        self,
        tenant_id: str,
        chat_id: str,
        site_id: str,
        default_site: bool = False,
    ) -> ChatBinding:
        binding = ChatBinding(
            tenant_id=tenant_id,
            chat_id=chat_id,
            site_id=site_id,
            default_site=default_site,
        )
        self._registry.bind_chat(binding)
        return binding

