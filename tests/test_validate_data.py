from pathlib import Path

from remote_venezuela_hiring.validate_data import validate_all


def test_sample_data_validates_clean():
    data_dir = Path(__file__).parents[1] / "data" / "companies"
    errors, _warnings = validate_all(data_dir)
    assert not errors, f"Sample data has validation errors: {errors}"


def test_invalid_yaml_produces_errors(tmp_path):
    bad = tmp_path / "bad-entry.yaml"
    bad.write_text(
        "id: bad-entry\n"
        "name: Bad Entry\n"
        "website: not-a-url\n"
        "status: accepts\n"
        "last_checked: 2026-05-15\n"
        "verification_method: unknown\n"
    )
    errors, _ = validate_all(tmp_path)
    assert errors, "Expected errors for invalid entry"


def test_filename_mismatch_produces_error(tmp_path):
    f = tmp_path / "wrong-name.yaml"
    f.write_text(
        "id: actual-id\n"
        "name: Test\n"
        "website: https://example.com\n"
        "status: unknown\n"
        "last_checked: 2026-05-15\n"
        "verification_method: unknown\n"
    )
    errors, _ = validate_all(tmp_path)
    assert any("does not match id" in e for e in errors)
