# SaaS AI-агент для Bitrix через Telegram

## 1. Цель

Построить SaaS-платформу, где Telegram-бот управляет **только**:
- контентом сайта (операции с инфоблоками),
- разрешенными настройками сайта,

и **не может** менять код проекта, шаблоны, PHP/JS/CSS файлы.

## 2. Основной сценарий взаимодействия

1. Пользователь в Telegram-чате пишет задачу.
2. Бот уточняет детали до формализуемой операции.
3. Бот показывает финальный план и ожидает подтверждение.
4. Пользователь отправляет `confirm`.
5. Бот выполняет команду в Bitrix и возвращает отчет.

В любой момент поддерживается `cancel`.

## 3. Multi-tenant / Multi-chat / Multi-site модель

Ключевые сущности:

- **Tenant** — клиент SaaS (компания/проект).
- **SiteBinding** — подключенный сайт Bitrix (URL + API token + профиль прав).
- **ChatBinding** — привязка Telegram-чата к сайту.
- **PermissionProfile** — границы операций:
  - список разрешенных инфоблоков,
  - уровень изменения настроек (`none/limited/full`),
  - allow-list префиксов настроек (для `limited`).

Это позволяет:
- подключать много сайтов для одного tenant,
- подключать много чатов к одному или разным сайтам,
- задавать отдельные права под каждый сайт.

## 4. Компоненты решения

1. **Telegram Gateway**
   - принимает апдейты,
   - маршрутизирует команды (`confirm`, `cancel`, обычный текст).

2. **Planner/Orchestrator**
   - превращает естественный язык в структурированные операции,
   - переводит задачу по state-machine:
     `draft -> need_clarification -> awaiting_confirmation -> executing -> done/failed`.

3. **Policy Engine (обязательный контроль)**
   - проверяет каждую операцию по allow-list,
   - блокирует любые code-level действия.

4. **Bitrix Connector**
   - исполняет только безопасные операции:
     - `update/create/delete` элемента инфоблока,
     - изменение разрешенных настроек.

5. **Bitrix Module `vendor.aiagent` (D7)**
   - модульная установка через `local/modules/vendor.aiagent`,
   - webhook endpoint `/bitrix/tools/vendor.aiagent/webhook.php`,
   - страница `options.php` для выдачи прав по инфоблокам и настройкам,
   - policy enforcement на стороне сайта (финальный контроль перед применением).

## 5. Границы безопасности (обязательно)

### Запрещено
- запись/изменение файлов;
- редактирование PHP/JS/CSS/шаблонов;
- выполнение shell-команд на хосте;
- любые операции вне allow-list.

### Обязательно
- подтверждение пользователя перед выполнением;
- аудит лог (кто, когда, что запросил/подтвердил/выполнил);
- site-scoped API токены;
- принцип минимальных прав.

## 6. Контракты API (MVP)

### Telegram payload (вход)
- `tenant_id`, `chat_id`, `user_id`, `text`.

### Ответ бота (выход)
- `text`,
- `state`: `need_clarification | awaiting_confirmation | done | failed`.

### Admin panel actions
- `upsert_site_access(...)` — обновить доступ сайта и профиль прав.
- `bind_chat_to_site(...)` — привязать чат к сайту.

## 7. Что реализовано в текущем MVP

- доменные модели multi-tenant;
- state-machine сценария подтверждения;
- policy engine с запретом изменения кода;
- контроллер Telegram-команд;
- каркас Bitrix-модуля по стандартам (`local/modules/vendor.aiagent`);
- unit-тесты критичных сценариев.

## 8. Production roadmap

1. Заменить deterministic planner на LLM + function calling.
2. Подключить БД (PostgreSQL) и очередь задач (Redis/RabbitMQ).
3. Реализовать реальный Bitrix REST connector.
4. Добавить web UI SaaS-админки и Bitrix-модуль интеграции.
5. Включить аудит, rate limit, alerting, SIEM-интеграцию.

