<?php

namespace Vendor\Aiagent;

use Bitrix\Main\Config\Option;
use Bitrix\Main\Loader;
use CIBlockElement;
use Vendor\Aiagent\Access\SiteAccessRepository;
use Vendor\Aiagent\Security\OperationPolicy;

final class Application
{
    private const MODULE_ID = "vendor.aiagent";

    private SiteAccessRepository $profiles;
    private OperationPolicy $policy;

    public function __construct(?SiteAccessRepository $profiles = null, ?OperationPolicy $policy = null)
    {
        $this->profiles = $profiles ?? new SiteAccessRepository();
        $this->policy = $policy ?? new OperationPolicy();
    }

    /**
     * @param array<string, mixed> $operation
     * @return array<string, mixed>
     */
    public function executeOperation(array $operation): array
    {
        $siteId = (string)($operation["site_id"] ?? "");
        if ($siteId === "") {
            throw new \InvalidArgumentException("site_id обязателен.");
        }

        $profile = $this->profiles->getProfile($siteId);
        $this->policy->assertAllowed($operation, $profile);

        $type = (string)$operation["operation_type"];
        switch ($type) {
            case "update_iblock_element":
                return $this->updateIblockElement($operation);
            case "create_iblock_element":
                return $this->createIblockElement($operation);
            case "delete_iblock_element":
                return $this->deleteIblockElement($operation);
            case "update_site_setting":
                return $this->updateSiteSetting($operation);
            default:
                throw new \RuntimeException("Операция не поддерживается.");
        }
    }

    /**
     * @param array<string, mixed> $operation
     * @return array<string, mixed>
     */
    private function updateIblockElement(array $operation): array
    {
        if (!Loader::includeModule("iblock")) {
            throw new \RuntimeException("Модуль iblock не подключен.");
        }

        $elementId = (int)($operation["target"]["element_id"] ?? 0);
        $field = (string)($operation["payload"]["field"] ?? "");
        $value = (string)($operation["payload"]["value"] ?? "");

        if ($elementId <= 0 || $field === "") {
            throw new \InvalidArgumentException("Недостаточно данных для обновления элемента.");
        }

        $el = new CIBlockElement();
        $updated = $el->Update($elementId, [$field => $value]);
        if (!$updated) {
            throw new \RuntimeException((string)$el->LAST_ERROR ?: "Ошибка обновления элемента инфоблока.");
        }

        return [
            "success" => true,
            "message" => "Элемент " . $elementId . " обновлен.",
        ];
    }

    /**
     * @param array<string, mixed> $operation
     * @return array<string, mixed>
     */
    private function createIblockElement(array $operation): array
    {
        if (!Loader::includeModule("iblock")) {
            throw new \RuntimeException("Модуль iblock не подключен.");
        }

        $iblockId = (int)($operation["target"]["iblock_id"] ?? 0);
        $name = (string)($operation["payload"]["name"] ?? "");

        if ($iblockId <= 0 || $name === "") {
            throw new \InvalidArgumentException("Недостаточно данных для создания элемента.");
        }

        $el = new CIBlockElement();
        $elementId = $el->Add([
            "IBLOCK_ID" => $iblockId,
            "NAME" => $name,
            "ACTIVE" => "Y",
        ]);
        if (!$elementId) {
            throw new \RuntimeException((string)$el->LAST_ERROR ?: "Ошибка создания элемента инфоблока.");
        }

        return [
            "success" => true,
            "message" => "Создан элемент " . $elementId . ".",
            "element_id" => (int)$elementId,
        ];
    }

    /**
     * @param array<string, mixed> $operation
     * @return array<string, mixed>
     */
    private function deleteIblockElement(array $operation): array
    {
        if (!Loader::includeModule("iblock")) {
            throw new \RuntimeException("Модуль iblock не подключен.");
        }

        $elementId = (int)($operation["target"]["element_id"] ?? 0);
        if ($elementId <= 0) {
            throw new \InvalidArgumentException("Не указан element_id.");
        }

        $deleted = CIBlockElement::Delete($elementId);
        if (!$deleted) {
            throw new \RuntimeException("Ошибка удаления элемента инфоблока.");
        }

        return [
            "success" => true,
            "message" => "Элемент " . $elementId . " удален.",
        ];
    }

    /**
     * @param array<string, mixed> $operation
     * @return array<string, mixed>
     */
    private function updateSiteSetting(array $operation): array
    {
        $siteId = (string)($operation["site_id"] ?? "");
        $key = (string)($operation["target"]["setting_key"] ?? "");
        $value = (string)($operation["payload"]["value"] ?? "");
        if ($key === "") {
            throw new \InvalidArgumentException("Не указан setting_key.");
        }

        Option::set(self::MODULE_ID, $key, $value, $siteId);

        return [
            "success" => true,
            "message" => "Настройка " . $key . " обновлена.",
        ];
    }
}

