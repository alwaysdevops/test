from app import validate_registration


def test_validate_registration_accepts_valid_data():
    errors = validate_registration(
        {"name": "Asha Rao", "email": "asha@example.com", "event": "Cloud Workshop"}
    )

    assert errors == []


def test_validate_registration_rejects_missing_and_invalid_data():
    errors = validate_registration({"name": "", "email": "bad-email", "event": ""})

    assert "Name is required." in errors
    assert "Enter a valid email address." in errors
    assert "Event name is required." in errors
