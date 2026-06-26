from rich._pick import pick_bool


def test_pick_bool():
    assert pick_bool(False) == False
    assert pick_bool(True) == True
    assert pick_bool(None) == False
    assert pick_bool(False, True) == False
    assert pick_bool(None, True) == True
    assert pick_bool(True, None) == True
    assert pick_bool(False, None) == False
    assert pick_bool(None, None) == False
    assert pick_bool(None, None, False, True) == False
    assert pick_bool(None, None, True, False) == True


def test_pick_bool_returns_bool_type():
    """pick_bool must always return a real bool, even when inputs are not bools.

    The previous implementation leaked the loop variable and returned it
    unconverted when all values were None, and only wrapped non-None values in
    bool() when the loop returned early. This meant pick_bool(None, "hello")
    returned the string "hello" rather than True, breaking downstream code that
    relies on a real bool (e.g. `pick_bool(...) or overflow == "ignore"` in
    rich.text.Text.wrap).
    """
    # All-None inputs: must coerce to bool, not return None.
    assert pick_bool(None) is False
    assert pick_bool(None, None) is False
    assert pick_bool(None, None, None) is False
    assert isinstance(pick_bool(None), bool)
    assert isinstance(pick_bool(None, None, None), bool)

    # Non-bool truthy inputs: must coerce, not return the original object.
    assert pick_bool(None, "hello") is True
    assert pick_bool(None, 42) is True
    assert pick_bool(None, [1, 2]) is True
    assert pick_bool(None, "hello") == True
    assert isinstance(pick_bool(None, "hello"), bool)

    # Non-bool falsy inputs: must coerce, not return the original object.
    assert pick_bool(None, 0) is False
    assert pick_bool(None, "") is False
    assert pick_bool(None, []) is False
    assert isinstance(pick_bool(None, 0), bool)

    # First non-None value still wins, but is wrapped as bool explicitly.
    assert isinstance(pick_bool(None, 1, False), bool)
    assert isinstance(pick_bool(None, 0, True), bool)
