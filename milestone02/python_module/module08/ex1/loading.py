#!/usr/bin/env python3

import sys
import importlib.metadata

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def get_version(package: str) -> str:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def check_dependencies() -> bool:
    packages = ["pandas", "numpy", "matplotlib"]
    all_ok = True

    print("Checking dependencies:")
    for pkg in packages:
        version = get_version(pkg)
        if version == "not installed":
            print(f"[KO] {pkg} - not installed")
            all_ok = False
        else:
            print(f"[OK] {pkg} ({version}) - ready")

    return all_ok


def show_install_instructions() -> None:
    print()
    print("To install dependencies:")
    print()
    print("  Using pip:")
    print("    pip install -r requirements.txt")
    print()
    print("  Using Poetry:")
    print("    poetry install")
    print("    poetry run python loading.py")


def analyze_matrix_data() -> None:
    print()
    print("Analyzing Matrix data...")

    data = np.random.randn(1000)
    print(f"Processing {len(data)} data points...")

    series = pd.Series(data, name="Matrix Signal")
    print()
    print("Generating visualization...")
    print(series.describe().to_string())
    labels = [
        "Strong Negative", "Weak Negative",
        "Weak Positive", "Strong Positive",
    ]
    counts = [
        int((data < -1).sum()),
        int(((data >= -1) & (data < 0)).sum()),
        int(((data >= 0) & (data < 1)).sum()),
        int((data >= 1).sum()),
    ]
    fig, ax = plt.subplots()
    colors = ["#49bb23", "#9a2372", "#AABE3C", "#2d707e"]
    ax.pie(counts, labels=labels, autopct="%1.1f%%", colors=colors)
    ax.set_title("Matrix Signal Distribution")
    plt.savefig("matrix_analysis.png")
    plt.close(fig)
    print()
    print("Analysis complete!")
    print("Results saved to: matrix_analysis.png")


def main() -> None:
    print("LOADING STATUS: Loading programs...")
    print()
    all_ok = check_dependencies()
    if not all_ok:
        show_install_instructions()
        sys.exit(1)
    analyze_matrix_data()


if __name__ == "__main__":
    main()
