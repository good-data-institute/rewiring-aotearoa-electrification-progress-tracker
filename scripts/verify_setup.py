"""Verify project setup and configuration.

This script checks that all components are correctly installed and configured.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(
            f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.12+)"
        )
        return False


def check_imports():
    """Check if all required packages are installed."""
    packages = {
        "pandas": "pandas",
        "pydantic": "pydantic",
        "pydantic_settings": "pydantic-settings",
        "requests": "requests",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "duckdb": "duckdb",
        "streamlit": "streamlit",
        "shiny": "shiny",
        "dotenv": "python-dotenv",
        "ruff": "ruff (dev)",
        "pytest": "pytest (dev)",
    }

    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - not installed")
            all_ok = False

    return all_ok


def check_files():
    """Check if all required files exist."""
    required_files = [
        ".env",
        ".gitignore",
        ".pre-commit-config.yaml",
        "pyproject.toml",
        "README.md",
    ]

    all_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            if file == ".env":
                print(f"✗ {file} - missing (copy .env.example to .env)")
            else:
                print(f"✗ {file} - missing")
            all_ok = False

    return all_ok


def check_directories():
    """Check if data directories exist."""
    from pathlib import Path

    # Add project root to Python path
    project_root = Path(__file__).resolve().parent.parent  # adjust if script is nested
    sys.path.append(str(project_root))

    from etl.core.config import get_settings

    settings = get_settings()
    directories = [
        settings.data_dir,
    ]

    all_ok = True
    for directory in directories:
        if directory.exists():
            print(f"✓ {directory}")
        else:
            print(f"✗ {directory} - missing (will be created on first run)")
            all_ok = False

    return all_ok


def check_env_file():
    """Check .env file configuration."""
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env file not found")
        return False

    required_vars = [
        "DATA_DIR",
        "BACKEND_HOST",
        "BACKEND_PORT",
    ]

    content = env_file.read_text(encoding="utf-8")
    all_ok = True
    for var in required_vars:
        if var in content:
            print(f"✓ {var} configured")
        else:
            print(f"✗ {var} missing from .env")
            all_ok = False

    return all_ok


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("PROJECT SETUP VERIFICATION")
    print("=" * 80)

    checks = {
        "Python Version": check_python_version,
        "Required Packages": check_imports,
        "Project Files": check_files,
        "Environment Configuration": check_env_file,
        "Data Directories": check_directories,
    }

    results = {}
    for name, check_func in checks.items():
        print(f"\n{name}:")
        print("-" * 40)
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Check failed with error: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    all_passed = all(results.values())

    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    if all_passed:
        print("\n🎉 All checks passed! Project is ready to use.")
        print("\nNext steps:")
        print("1. Run ETL pipeline: python run_pipeline.py")
        print("2. Start backend: python -m backend.main")
        print("3. Launch dashboard: streamlit run frontend/streamlit_app.py")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("\nTo fix:")
        print("1. Ensure virtual environment is activated")
        print("2. Sync dependencies: uv sync")
        print("3. Copy .env.example to .env if missing")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
