from remote_venezuela_hiring.slugify import slugify


def test_lowercases():
    assert slugify("Acme") == "acme"


def test_replaces_spaces_with_hyphens():
    assert slugify("My Cool Company") == "my-cool-company"


def test_collapses_multiple_spaces():
    assert slugify("My   Cool   Company") == "my-cool-company"


def test_strips_special_characters():
    assert slugify("Foo, Inc.!") == "foo-inc"


def test_handles_already_kebab_case():
    assert slugify("already-kebab") == "already-kebab"


def test_strips_leading_and_trailing_hyphens():
    assert slugify("  -Hello-  ") == "hello"
