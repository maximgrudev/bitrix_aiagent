<?php

use Bitrix\Main\Loader;
use Vendor\Aiagent\Integration\WebhookHandler;

require_once $_SERVER["DOCUMENT_ROOT"] . "/bitrix/modules/main/include/prolog_before.php";

header("Content-Type: application/json; charset=UTF-8");

try {
    if (!Loader::includeModule("vendor.aiagent")) {
        throw new RuntimeException("Модуль vendor.aiagent не установлен.");
    }

    $rawBody = file_get_contents("php://input");
    if (!is_string($rawBody)) {
        throw new RuntimeException("Не удалось прочитать тело запроса.");
    }

    $payload = json_decode($rawBody, true);
    if (!is_array($payload)) {
        throw new RuntimeException("Некорректный JSON payload.");
    }

    $signature = (string)($_SERVER["HTTP_X_AIAGENT_SIGNATURE"] ?? "");
    $handler = new WebhookHandler();
    $result = $handler->handle($payload, $signature, $rawBody);

    echo json_encode(
        ["ok" => true, "result" => $result],
        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
    );
} catch (Throwable $exception) {
    http_response_code(400);
    echo json_encode(
        ["ok" => false, "error" => $exception->getMessage()],
        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
    );
}

