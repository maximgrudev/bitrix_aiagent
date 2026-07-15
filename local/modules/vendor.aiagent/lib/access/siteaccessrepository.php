<?php

namespace Vendor\Aiagent\Access;

use Bitrix\Main\Config\Option;
use Bitrix\Main\SiteTable;

final class SiteAccessRepository
{
    private const MODULE_ID = "vendor.aiagent";
    private const OPTION_KEY = "site_profiles_json";

    /**
     * @return array<string, SiteAccessProfile>
     */
    public function getAllProfiles(): array
    {
        $rawJson = (string)Option::get(self::MODULE_ID, self::OPTION_KEY, "{}");
        $decoded = json_decode($rawJson, true);
        $profilesData = is_array($decoded) ? $decoded : [];

        $profiles = [];
        $sites = SiteTable::getList(["select" => ["LID"]]);
        while ($site = $sites->fetch()) {
            $siteId = (string)$site["LID"];
            $siteData = $profilesData[$siteId] ?? [];
            $profiles[$siteId] = new SiteAccessProfile(
                $siteId,
                is_array($siteData["allowed_iblocks"] ?? null) ? $siteData["allowed_iblocks"] : [],
                (string)($siteData["settings_access"] ?? "none"),
                is_array($siteData["allowed_setting_prefixes"] ?? null) ? $siteData["allowed_setting_prefixes"] : []
            );
        }

        return $profiles;
    }

    public function getProfile(string $siteId): SiteAccessProfile
    {
        $profiles = $this->getAllProfiles();
        return $profiles[$siteId] ?? new SiteAccessProfile($siteId, [], "none", []);
    }

    public function saveProfile(SiteAccessProfile $profile): void
    {
        $rawJson = (string)Option::get(self::MODULE_ID, self::OPTION_KEY, "{}");
        $decoded = json_decode($rawJson, true);
        $profiles = is_array($decoded) ? $decoded : [];
        $profiles[$profile->getSiteId()] = $profile->toArray();
        Option::set(
            self::MODULE_ID,
            self::OPTION_KEY,
            json_encode($profiles, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
        );
    }
}

