"""Rule that maps a character id to the (1-based) position of the image to pick."""


def image_position(character_id: int) -> int:
    """Hundreds digit + ones digit for ids with 3+ digits; tens digit + ones digit otherwise.

        123 -> 1 + 3 = 4      45 -> 4 + 5 = 9      7 -> 0 + 7 = 7      826 -> 8 + 6 = 14

    Ids with 4+ digits use the same hundreds + ones rule (not defined by the task; the API
    currently has < 1000 characters). A result of 0 (e.g. id 1000) is not a valid 1-based
    position, so it raises instead of silently picking something.
    """
    if isinstance(character_id, bool) or not isinstance(character_id, int):
        raise TypeError(f"Character id must be an int, got {character_id!r}")
    if character_id < 1:
        raise ValueError(f"Character id must be positive, got {character_id}")

    ones = character_id % 10
    leading_digit = (character_id // 100) % 10 if character_id >= 100 else (character_id // 10) % 10
    position = leading_digit + ones
    if position == 0:
        raise ValueError(f"Character id {character_id} yields image position 0; positions start at 1")
    return position