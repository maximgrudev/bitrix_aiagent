<?php

namespace Vendor\Aiagent\Security;

use Vendor\Aiagent\Access\SiteAccessProfile;

final class OperationPolicy
{
    private const ALLOWED_TYPES = [
        "update_iblock_element",
        "create_iblock_element",
        "delete_iblock_element",
        "update_site_setting",
    ];

    /**
     * @param array<string, mixed> $operation
     */
    public function assertAllowed(array $operation, SiteAccessProfile $profile): void
    {
        $scope = (string)($operation["scope"] ?? "");
        $type = (string)($operation["operation_type"] ?? "");

        if ($scope === "code" || $type === "touch_code") {
            throw new \RuntimeException("Изменение кода запрещено политикой модуля.");
        }

        if (!in_array($type, self::ALLOWED_TYPES, true)) {
            throw new \RuntimeException("Операция не входит в allow-list модуля.");
        }

        if (in_array($type, ["update_iblock_element", "create_iblock_element", "delete_iblock_element"], true)) {
            $iblockId = (int)($operation["target"]["iblock_id"] ?? 0);
            if ($iblockId <= 0) {
                throw new \RuntimeException("Не указан iblock_id.");
            }
            if (!in_array($iblockId, $profile->getAllowedIblocks(), true)) {
                throw new \RuntimeException("Нет прав на инфоблок " . $iblockId . ".");
            }
        }

        if ($type === "update_site_setting") {
            $level = $profile->getSettingsAccess();
            if ($level === "none") {
                throw new \RuntimeException("Редактирование настроек запрещено для сайта.");
            }

            $key = (string)($operation["target"]["setting_key"] ?? "");
            if ($key === "") {
                throw new \RuntimeException("Не указан ключ настройки.");
            }

            if ($level === "limited") {
                $allowed = false;
                foreach ($profile->getAllowedSettingPrefixes() as $prefix) {
                    if ($prefix !== "" && mb_strpos($key, $prefix) === 0) {
                        $allowed = true;
                        break;
                    }
                }
                if (!$allowed) {
                    throw new \RuntimeException("Настройка " . $key . " не разрешена политикой сайта.");
                }
            }
        }
    }
}

