# bitrix_aiagent

MVP-каркас SaaS AI-агента для управления сайтами Bitrix через Telegram.

## Что умеет MVP

- поддержка модели many-sites x many-chats;
- workflow: уточнение -> финальный план -> подтверждение -> выполнение;
- строгое ограничение операций:
  - разрешены только контент (инфоблоки) и разрешенные настройки;
  - изменение кода сайта запрещено политикой.

## Структура

- `src/bitrix_aiagent/domain.py` — доменные сущности и состояния.
- `src/bitrix_aiagent/policy.py` — policy engine и проверки прав.
- `src/bitrix_aiagent/planner.py` — MVP-планировщик команд.
- `src/bitrix_aiagent/workflow.py` — state-machine оркестрации.
- `src/bitrix_aiagent/telegram.py` — Telegram-контроллер.
- `src/bitrix_aiagent/admin_panel.py` — слой “панели доступа” сайта.
- `src/bitrix_aiagent/bitrix.py` — адаптер Bitrix (in-memory MVP).
- `docs/saas-bitrix-telegram-architecture.md` — целевая архитектура.

## Локальный запуск демо

```bash
PYTHONPATH=src python3 -m bitrix_aiagent.app
```

## Тесты

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
