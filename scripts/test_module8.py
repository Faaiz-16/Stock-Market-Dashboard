"""
Module 8 test script — Deployment & Documentation

Verifies the project is deployment-ready and documentation is complete.

Run from the project root:

    python scripts/test_module8.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_project_structure() -> None:
    """Verify all required project files and folders exist."""
    print_section("TEST 1: Final Project Structure")

    required_paths = [
        "app.py",
        "requirements.txt",
        "runtime.txt",
        "README.md",
        ".gitignore",
        ".streamlit/config.toml",
        "config/settings.py",
        "src/data_fetcher.py",
        "src/data_processor.py",
        "src/analytics.py",
        "src/pipeline.py",
        "src/exceptions.py",
        "src/ui/layout.py",
        "src/ui/sidebar.py",
        "src/ui/header.py",
        "src/ui/stats_cards.py",
        "src/ui/analytics_cards.py",
        "src/ui/charts.py",
        "src/ui/chart_renderer.py",
        "src/ui/styles.py",
        "docs/screenshots/.gitkeep",
    ]

    for rel_path in required_paths:
        full_path = PROJECT_ROOT / rel_path
        assert full_path.exists(), f"Missing: {rel_path}"
        print(f"  ✅ {rel_path}")

    print("✅ Final project structure is complete")


def test_requirements() -> None:
    """Verify requirements.txt contains all mandatory packages."""
    print_section("TEST 2: Dependencies (requirements.txt)")

    content = (PROJECT_ROOT / "requirements.txt").read_text()
    required_packages = [
        "streamlit",
        "pandas",
        "requests",
        "plotly",
        "curl_cffi",
    ]

    for package in required_packages:
        assert package in content, f"Missing package: {package}"
        print(f"  ✅ {package}")

    print("✅ All required packages listed")


def test_readme_documentation() -> None:
    """Verify README contains key deployment and documentation sections."""
    print_section("TEST 3: README Documentation")

    readme = (PROJECT_ROOT / "README.md").read_text()
    required_sections = [
        "Installation Guide",
        "Execution Guide",
        "GitHub Upload Instructions",
        "Screenshots to Take",
        "Deployment",
        "Troubleshooting",
        "Final Project Structure",
    ]

    for section in required_sections:
        assert section in readme, f"README missing section: {section}"
        print(f"  ✅ {section}")

    assert "Deployment & Documentation" in readme and "✅ Complete" in readme
    print("  ✅ Module 8 marked complete")
    print("✅ README documentation is complete")


def test_gitignore() -> None:
    """Verify .gitignore protects secrets and local artifacts."""
    print_section("TEST 4: .gitignore")

    gitignore = (PROJECT_ROOT / ".gitignore").read_text()
    required_entries = ["venv/", "__pycache__/", ".env", "secrets.toml"]

    for entry in required_entries:
        assert entry in gitignore, f".gitignore missing: {entry}"
        print(f"  ✅ {entry}")

    print("✅ .gitignore is configured correctly")


def test_streamlit_config() -> None:
    """Verify Streamlit config exists for deployment."""
    print_section("TEST 5: Streamlit Config")

    config = (PROJECT_ROOT / ".streamlit/config.toml").read_text()
    assert "[theme]" in config, "Missing [theme] section"
    assert "[server]" in config, "Missing [server] section"
    print("  ✅ [theme] section")
    print("  ✅ [server] section")
    print("✅ Streamlit config is deployment-ready")


def test_all_module_scripts() -> None:
    """Verify all module test scripts exist."""
    print_section("TEST 6: Module Test Scripts")

    for i in range(2, 9):
        script = PROJECT_ROOT / "scripts" / f"test_module{i}.py"
        assert script.exists(), f"Missing: scripts/test_module{i}.py"
        print(f"  ✅ test_module{i}.py")

    print("✅ All module test scripts present")


def test_app_entry_point() -> None:
    """Verify the app entry point is ready for deployment."""
    print_section("TEST 7: App Entry Point")

    import app  # noqa: F401

    assert hasattr(app, "main"), "app.py missing main()"
    assert hasattr(app, "configure_page"), "app.py missing configure_page()"
    print("  ✅ app.py imports successfully")
    print("  ✅ main() and configure_page() defined")
    print("✅ App is ready for `streamlit run app.py`")


def main() -> None:
    """Run all Module 8 deployment and documentation tests."""
    print("Starting Module 8 tests for Deployment & Documentation...")

    tests = [
        test_project_structure,
        test_requirements,
        test_readme_documentation,
        test_gitignore,
        test_streamlit_config,
        test_all_module_scripts,
        test_app_entry_point,
    ]

    for test in tests:
        test()

    print_section("ALL MODULE 8 TESTS PASSED ✅")
    print("\n🎉 Project is deployment-ready!")
    print("   Local:      streamlit run app.py")
    print("   GitHub:     see README → GitHub Upload Instructions")
    print("   Deploy:     see README → Deployment (Streamlit Community Cloud)")


if __name__ == "__main__":
    main()
