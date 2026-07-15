# Bitrix-модуль `vendor.aiagent` (D7)

Этот каталог оформляет часть на стороне сайта как модуль Битрикс по стандартной структуре:

`local/modules/vendor.aiagent/`

## Структура

- `install/index.php` — установщик/деинсталлятор модуля.
- `install/version.php` — версия модуля.
- `include.php` — регистрация автозагрузки классов.
- `lib/` — бизнес-логика D7:
  - `Application` — исполняет разрешенные операции;
  - `Security/OperationPolicy` — enforce allow-list, запрет code-операций;
  - `Access/SiteAccessRepository` — хранение прав по сайтам;
  - `Integration/WebhookHandler` — HMAC-валидация входящих команд.
- `options.php` — страница настроек модуля в админке:
  - webhook secret;
  - разрешенные инфоблоки по каждому сайту;
  - уровень доступа к настройкам (`none/limited/full`);
  - allow-list префиксов настроек.
- `install/tools/vendor.aiagent/webhook.php` — endpoint для SaaS-команд.
- `admin/vendor_aiagent_options.php` + `install/admin/...` — подключение страницы опций в `/bitrix/admin`.
- `lang/ru/*` — локализация.

## Установка

1. Скопировать модуль в `local/modules/vendor.aiagent`.
2. В админке Битрикс установить модуль `vendor.aiagent`.
3. Открыть настройки модуля и заполнить:
   - `webhook_secret`;
   - права по инфоблокам;
   - уровень доступа к настройкам и префиксы.

## Endpoint

- URL: `/bitrix/tools/vendor.aiagent/webhook.php`
- Method: `POST`
- Header: `X-AIAGENT-Signature: <hex-hmac-sha256(rawBody, webhook_secret)>`
- Body: JSON операции.

Пример payload:

```json
{
  "site_id": "s1",
  "scope": "content",
  "operation_type": "update_iblock_element",
  "target": {
    "iblock_id": 12,
    "element_id": 44
  },
  "payload": {
    "field": "NAME",
    "value": "Новый заголовок"
  }
}
```

## Ограничения безопасности

- любые попытки изменения кода блокируются;
- обрабатываются только allow-list операции:
  - `update_iblock_element`
  - `create_iblock_element`
  - `delete_iblock_element`
  - `update_site_setting`
- настройки ограничиваются уровнем доступа и allow-list префиксами.

