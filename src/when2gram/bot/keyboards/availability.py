from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from when2gram.domain.availability import SLOTS_PER_DAY, is_selected

HEADER_STYLE = "primary"
SUCCESS_STYLE = "success"
PRIMARY_STYLE = "primary"


def _availability_style(count: int, respondent_count: int) -> str | None:
    if respondent_count <= 0 or count <= 0:
        return None
    ratio = count / respondent_count
    if ratio >= 0.70:
        return SUCCESS_STYLE
    if ratio >= 0.40:
        return PRIMARY_STYLE
    return None


def availability_keyboard(
    counts: Sequence[int],
    *,
    respondent_count: int,
    selected_mask: int = 0,
) -> InlineKeyboardMarkup:
    if len(counts) != SLOTS_PER_DAY:
        raise ValueError(f"expected {SLOTS_PER_DAY} counts, got {len(counts)}")

    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="", callback_data="noop", style=HEADER_STYLE),
            InlineKeyboardButton(text=":00", callback_data="noop", style=HEADER_STYLE),
            InlineKeyboardButton(text=":15", callback_data="noop", style=HEADER_STYLE),
            InlineKeyboardButton(text=":30", callback_data="noop", style=HEADER_STYLE),
            InlineKeyboardButton(text=":45", callback_data="noop", style=HEADER_STYLE),
        ]
    ]

    for hour_offset, hour in enumerate(range(9, 24)):
        row = [InlineKeyboardButton(text=f"{hour:02d}", callback_data="noop", style=HEADER_STYLE)]
        for quarter in range(4):
            slot = hour_offset * 4 + quarter
            count = counts[slot]
            marker = "✓" if is_selected(selected_mask, slot) else ""
            row.append(
                InlineKeyboardButton(
                    text=f"{marker}{count}",
                    callback_data=f"slot:{slot}",
                    style=_availability_style(count, respondent_count),
                )
            )
        rows.append(row)

    rows.append(
        [
            InlineKeyboardButton(text="Clear", callback_data="grid:clear", style="danger"),
            InlineKeyboardButton(text="Done", callback_data="grid:done", style="success"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
