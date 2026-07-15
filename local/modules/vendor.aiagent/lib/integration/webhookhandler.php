<?php

namespace Vendor\Aiagent\Integration;

use Bitrix\Main\Config\Option;
use Vendor\Aiagent\Application;

final class WebhookHandler
{
    private const MODULE_ID = "vendor.aiagent";
    private const SECRET_OPTION = "webhook_secret";

    private Application $application;

    public function __construct(?Application $application = null)
    {
        $this->application = $application ?? new Application();
    }

    /**
     * @param array<string, mixed> $payload
     * @return array<string, mixed>
     */
    public function handle(array $payload, string $signature, string $rawBody): array
    {
        $this->assertSignature($signature, $rawBody);
        return $this->application->executeOperation($payload);
    }

    private function assertSignature(string $signature, string $rawBody): void
    {
        $secret = (string)Option::get(self::MODULE_ID, self::SECRET_OPTION, "");
        if ($secret === "") {
            throw new \RuntimeException("Webhook secret не настроен в модуле.");
        }

        $expected = hash_hmac("sha256", $rawBody, $secret);
        if (!hash_equals($expected, $signature)) {
            throw new \RuntimeException("Некорректная подпись webhook.");
        }
    }
}

