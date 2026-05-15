from pathlib import Path

from remote_venezuela_hiring.load_data import load_all_companies, load_company

DATA_DIR = Path(__file__).parents[1] / "data" / "companies"


def test_all_sample_yaml_files_load():
    companies = load_all_companies(DATA_DIR)
    assert len(companies) >= 9


def test_companies_sorted_by_name_case_insensitive():
    companies = load_all_companies(DATA_DIR)
    names = [c.name.lower() for c in companies]
    assert names == sorted(names)


def test_each_file_id_matches_filename():
    for path in sorted(DATA_DIR.glob("*.yaml")):
        company = load_company(path)
        assert path.stem == company.id, f"Filename '{path.stem}' does not match id '{company.id}'"


def test_load_company_returns_model_instance():
    sample = next(DATA_DIR.glob("*.yaml"))
    company = load_company(sample)
    assert company.name
    assert str(company.website).startswith("http")
