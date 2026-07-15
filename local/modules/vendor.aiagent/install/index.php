<?php

use Bitrix\Main\Localization\Loc;
use Bitrix\Main\ModuleManager;
use Bitrix\Main\Config\Option;

Loc::loadMessages(__FILE__);

if (class_exists("vendor_aiagent")) {
    return;
}

class vendor_aiagent extends CModule
{
    public $MODULE_ID = "vendor.aiagent";
    public $MODULE_NAME;
    public $MODULE_DESCRIPTION;
    public $MODULE_VERSION;
    public $MODULE_VERSION_DATE;
    public $PARTNER_NAME;
    public $PARTNER_URI;

    public function __construct()
    {
        $moduleVersion = [];
        include __DIR__ . "/version.php";
        if (!empty($arModuleVersion) && is_array($arModuleVersion)) {
            $moduleVersion = $arModuleVersion;
        }

        $this->MODULE_VERSION = (string)($moduleVersion["VERSION"] ?? "0.0.1");
        $this->MODULE_VERSION_DATE = (string)($moduleVersion["VERSION_DATE"] ?? date("Y-m-d H:i:s"));
        $this->MODULE_NAME = Loc::getMessage("VENDOR_AIAGENT_MODULE_NAME");
        $this->MODULE_DESCRIPTION = Loc::getMessage("VENDOR_AIAGENT_MODULE_DESCRIPTION");
        $this->PARTNER_NAME = "AI Agent";
        $this->PARTNER_URI = "https://example.com";
    }

    public function DoInstall()
    {
        ModuleManager::registerModule($this->MODULE_ID);
        $this->InstallFiles();
        $this->InstallDB();
    }

    public function DoUninstall()
    {
        $this->UnInstallFiles();
        $this->UnInstallDB();
        ModuleManager::unRegisterModule($this->MODULE_ID);
    }

    public function InstallDB()
    {
        return true;
    }

    public function UnInstallDB()
    {
        Option::delete($this->MODULE_ID);
        return true;
    }

    public function InstallFiles()
    {
        CopyDirFiles(
            __DIR__ . "/admin",
            $_SERVER["DOCUMENT_ROOT"] . "/bitrix/admin",
            true,
            true
        );
        CopyDirFiles(
            __DIR__ . "/tools",
            $_SERVER["DOCUMENT_ROOT"] . "/bitrix/tools",
            true,
            true
        );

        return true;
    }

    public function UnInstallFiles()
    {
        DeleteDirFiles(
            __DIR__ . "/admin",
            $_SERVER["DOCUMENT_ROOT"] . "/bitrix/admin"
        );
        DeleteDirFiles(
            __DIR__ . "/tools",
            $_SERVER["DOCUMENT_ROOT"] . "/bitrix/tools"
        );

        return true;
    }
}

