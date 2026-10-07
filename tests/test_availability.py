import pytest

from when2gram.domain.availability import (
    ALL_SLOTS_MASK,
    SLOTS_PER_DAY,
    aggregate_counts,
    best_slots,
    clamp_mask,
    is_selected,
    slot_label,
    toggle_slot,
)


def test_day_has_60_slots() -> None:
    assert SLOTS_PER_DAY == 60
    assert slot_label(0) == "09:00"
    assert slot_label(59) == "23:45"


def test_toggle_slot_round_trip() -> None:
    mask = toggle_slot(0, 7)
    assert is_selected(mask, 7)
    assert toggle_slot(mask, 7) == 0


def test_clamp_mask_removes_bits_outside_day() -> None:
    assert clamp_mask(ALL_SLOTS_MASK | (1 << 63)) == ALL_SLOTS_MASK


def test_aggregate_counts() -> None:
    first = toggle_slot(toggle_slot(0, 0), 1)
    second = toggle_slot(toggle_slot(0, 1), 2)
    counts = aggregate_counts([first, second])
    assert counts[:4] == [1, 2, 1, 0]


def test_best_slots_tie_breaks_by_time() -> None:
    counts = [0] * SLOTS_PER_DAY
    counts[10] = 3
    counts[3] = 3
    counts[5] = 2
    assert best_slots(counts, limit=3) == [3, 10, 5]


def test_invalid_slot_rejected() -> None:
    with pytest.raises(ValueError):
        toggle_slot(0, SLOTS_PER_DAY)
