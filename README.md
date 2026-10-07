# When2Gram

Telegram-native, When2Meet-style group scheduling without a separate web app.

The project is intentionally Telegram-first: organizers create an event in the bot's private chat, share it through inline mode, and participants fill availability using an inline-keyboard timetable. Shared invitations are designed to update with the current response count and best-overlap preview.

## MVP scope

- 09:00–24:00 availability window at 15-minute resolution (60 slots/day)
- 15×4 time grid with row/column headers and styled count buttons
- When2Meet-like event creation across multiple dates
- inline invitations with live response count and a deep link to the bot's PM
- organizer-defined response threshold notification
- SQLite persistence
- `uv` for dependency management
- single-container `compose.yml` deployment

The first implementation slice includes the domain model, SQLite schema/migration, the 60-bit/day availability representation, and a `/grid` command for validating the dense Telegram keyboard UX before building the full event flow.

## Architecture

```text
Telegram
   |
   v
aiogram routers  ---> keyboard / inline adapters
   |
   v
application/domain logic
   |
   v
SQLAlchemy 2 async
   |
   v
SQLite (WAL, foreign keys, 5s busy timeout)
```

Each participant/day availability is represented as a 60-bit integer: bit 0 is 09:00 and bit 59 is 23:45. This keeps persistence and aggregation small while still allowing constant-time toggles.

## Local development

Requirements: Python 3.13+ and `uv`.

```bash
cp .env.example .env
# set BOT_TOKEN in .env
uv sync
uv run alembic upgrade head
uv run python -m when2gram
```

Try `/grid` in the bot's private chat to exercise the timetable prototype.

Run checks:

```bash
uv run ruff check .
uv run pytest
```

## Docker Compose

```bash
cp .env.example .env
# set BOT_TOKEN

docker compose up -d --build
```

The SQLite database is persisted in the named `when2gram-data` volume at `/data/when2gram.db`. Long polling is used, so no inbound port, reverse proxy, or TLS setup is required.

## Planned implementation order

1. Validate the availability grid on Telegram mobile and desktop clients.
2. Implement event creation and date selection.
3. Persist draft/submitted participant responses.
4. Add inline-mode invitations and deep links into PM.
5. Persist `inline_message_id` values and refresh shared invitations after submissions.
6. Add exactly-once response-threshold notifications.
7. Add integration tests around Telegram callbacks and SQLite concurrency.
