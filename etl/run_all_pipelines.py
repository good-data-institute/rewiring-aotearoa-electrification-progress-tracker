"""Run all ETL pipelines: Extract → Transform → Metrics.

Auto-discovers pipelines from directory structure. Continues execution even if pipelines fail.
"""

import importlib
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def run_pipeline(name: str, main_func):
    """Run a pipeline and track success/failure."""
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"{'='*80}")
    try:
        main_func()
        return True, None
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n✗ FAILED: {error_msg}")
        return False, error_msg


def discover_pipelines(pipelines_dir: Path, stage: str):
    """Discover pipeline modules dynamically.

    Args:
        pipelines_dir: Path to etl/pipelines directory
        stage: Pipeline stage ('extract' or 'transform')

    Returns:
        List of tuples: (display_name, module_path)
    """
    pipelines = []

    for source_dir in sorted(pipelines_dir.iterdir()):
        if source_dir.is_dir() and not source_dir.name.startswith("_"):
            stage_file = source_dir / f"{stage}.py"
            if stage_file.exists():
                source_name = source_dir.name.replace("_", " ").title()
                module_path = f"etl.pipelines.{source_dir.name}.{stage}"
                pipelines.append((f"{source_name} - {stage.title()}", module_path))

    return pipelines


def discover_metrics(pipelines_dir: Path):
    """Discover metric pipeline modules dynamically.

    Args:
        pipelines_dir: Path to etl/pipelines directory

    Returns:
        List of tuples: (display_name, module_path)
    """
    metrics = []

    for metric_file in sorted(pipelines_dir.glob("_*.py")):
        if metric_file.name != "__init__.py":
            metric_name = metric_file.stem
            module_path = f"etl.pipelines.{metric_name}"
            metrics.append((metric_name, module_path))

    return metrics


def main():
    """Execute all ETL pipelines."""
    results = []
    pipelines_dir = Path(__file__).parent / "pipelines"

    # ====================================================================
    # EXTRACT
    # ====================================================================
    print("\n" + "=" * 80)
    print("EXTRACT PHASE")
    print("=" * 80)

    for name, module_path in discover_pipelines(pipelines_dir, "extract"):
        module = importlib.import_module(module_path)
        results.append((name, *run_pipeline(name, module.main)))

    # ====================================================================
    # TRANSFORM
    # ====================================================================
    print("\n" + "=" * 80)
    print("TRANSFORM PHASE")
    print("=" * 80)

    for name, module_path in discover_pipelines(pipelines_dir, "transform"):
        module = importlib.import_module(module_path)
        results.append((name, *run_pipeline(name, module.main)))

    # ====================================================================
    # METRICS
    # ====================================================================
    print("\n" + "=" * 80)
    print("METRICS PHASE")
    print("=" * 80)

    for name, module_path in discover_metrics(pipelines_dir):
        module = importlib.import_module(module_path)
        results.append((name, *run_pipeline(name, module.main)))

    # ====================================================================
    # SUMMARY
    # ====================================================================
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    success = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print(f"\n✓ Successful: {len(success)}/{len(results)}")
    for name, _, _ in success:
        print(f"  ✓ {name}")

    if failed:
        print(f"\n✗ Failed: {len(failed)}/{len(results)}")
        for name, _, error in failed:
            print(f"  ✗ {name}")
            print(f"    {error}")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
