<?php

namespace Vendor\Aiagent\Access;

final class SiteAccessProfile
{
    private string $siteId;
    /** @var int[] */
    private array $allowedIblocks;
    private string $settingsAccess;
    /** @var string[] */
    private array $allowedSettingPrefixes;

    /**
     * @param int[] $allowedIblocks
     * @param string[] $allowedSettingPrefixes
     */
    public function __construct(
        string $siteId,
        array $allowedIblocks,
        string $settingsAccess,
        array $allowedSettingPrefixes
    ) {
        $this->siteId = $siteId;
        $this->allowedIblocks = array_values(array_unique(array_map("intval", $allowedIblocks)));
        $this->settingsAccess = $settingsAccess;
        $this->allowedSettingPrefixes = array_values(array_unique(array_filter($allowedSettingPrefixes)));
    }

    public function getSiteId(): string
    {
        return $this->siteId;
    }

    /**
     * @return int[]
     */
    public function getAllowedIblocks(): array
    {
        return $this->allowedIblocks;
    }

    public function getSettingsAccess(): string
    {
        return $this->settingsAccess;
    }

    /**
     * @return string[]
     */
    public function getAllowedSettingPrefixes(): array
    {
        return $this->allowedSettingPrefixes;
    }

    public function toArray(): array
    {
        return [
            "site_id" => $this->siteId,
            "allowed_iblocks" => $this->allowedIblocks,
            "settings_access" => $this->settingsAccess,
            "allowed_setting_prefixes" => $this->allowedSettingPrefixes,
        ];
    }
}

