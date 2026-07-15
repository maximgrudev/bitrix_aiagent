<?php

use Bitrix\Main\Loader;

Loader::registerAutoLoadClasses(
    "vendor.aiagent",
    [
        "Vendor\\Aiagent\\Application" => "lib/application.php",
        "Vendor\\Aiagent\\Security\\OperationPolicy" => "lib/security/operationpolicy.php",
        "Vendor\\Aiagent\\Access\\SiteAccessProfile" => "lib/access/siteaccessprofile.php",
        "Vendor\\Aiagent\\Access\\SiteAccessRepository" => "lib/access/siteaccessrepository.php",
        "Vendor\\Aiagent\\Integration\\WebhookHandler" => "lib/integration/webhookhandler.php",
    ]
);

