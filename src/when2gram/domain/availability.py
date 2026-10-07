from collections.abc import Iterable, Sequence
from datetime import time

START_MINUTE = 9 * 60
END_MINUTE = 24 * 60
SLOT_MINUTES = 15
SLOTS_PER_DAY = (END_MINUTE - START_MINUTE) // SLOT_MINUTES
ALL_SLOTS_MASK = (1 << SLOTS_PER_DAY) - 1


def validate_slot(slot: int) -> None:
    if not 0 <= slot < SLOTS_PER_DAY:
        raise ValueError(f"slot must be in [0, {SLOTS_PER_DAY}), got {slot}")


def toggle_slot(mask: int, slot: int) -> int:
    validate_slot(slot)
    return mask ^ (1 << slot)


def set_slot(mask: int, slot: int, selected: bool) -> int:
    validate_slot(slot)
    bit = 1 << slot
    return (mask | bit) if selected else (mask & ~bit)


def is_selected(mask: int, slot: int) -> bool:
    validate_slot(slot)
    return bool(mask & (1 << slot))


def clamp_mask(mask: int) -> int:
    if mask < 0:
        raise ValueError("availability mask cannot be negative")
    return mask & ALL_SLOTS_MASK


def slot_label(slot: int) -> str:
    validate_slot(slot)
    minute_of_day = START_MINUTE + slot * SLOT_MINUTES
    hour, minute = divmod(minute_of_day, 60)
    return f"{hour:02d}:{minute:02d}"


def slot_time(slot: int) -> time:
    label = slot_label(slot)
    hour, minute = map(int, label.split(":"))
    return time(hour=hour, minute=minute)


def aggregate_counts(masks: Iterable[int]) -> list[int]:
    counts = [0] * SLOTS_PER_DAY
    for raw_mask in masks:
        mask = clamp_mask(raw_mask)
        while mask:
            lowest_bit = mask & -mask
            slot = lowest_bit.bit_length() - 1
            counts[slot] += 1
            mask ^= lowest_bit
    return counts


def best_slots(counts: Sequence[int], *, limit: int = 5) -> list[int]:
    if len(counts) != SLOTS_PER_DAY:
        raise ValueError(f"expected {SLOTS_PER_DAY} counts, got {len(counts)}")
    if limit < 1:
        return []
    return sorted(range(SLOTS_PER_DAY), key=lambda slot: (-counts[slot], slot))[:limit]
