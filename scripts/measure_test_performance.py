#!/usr/bin/env python3
"""Performance measurement script for test execution.

This script measures the baseline performance of different test categories
to help evaluate the impact of parallel execution improvements.
"""

import subprocess
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def run_command(cmd: List[str]) -> Dict[str, Any]:
    """Run a command and measure its execution time."""
    print(f"Running: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        end_time = time.time()
        
        return {
            "command": " ".join(cmd),
            "duration": end_time - start_time,
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
            "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0,
            "output": result.stdout[-1000:] if result.stdout else "",  # Last 1000 chars
            "error": result.stderr[-1000:] if result.stderr else "",   # Last 1000 chars
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(cmd),
            "duration": 1800,
            "returncode": -1,
            "success": False,
            "timeout": True,
            "stdout_lines": 0,
            "stderr_lines": 0,
            "output": "",
            "error": "Command timed out after 30 minutes",
        }
    except Exception as e:
        return {
            "command": " ".join(cmd),
            "duration": 0,
            "returncode": -1,
            "success": False,
            "error": str(e),
            "stdout_lines": 0,
            "stderr_lines": 0,
            "output": "",
        }


def measure_test_categories() -> Dict[str, Any]:
    """Measure performance of different test categories."""
    
    # Ensure we're in the project root
    if not Path("pyproject.toml").exists():
        raise RuntimeError("Must run from project root (where pyproject.toml exists)")
    
    base_cmd = ["uv", "run", "pytest", "-v"]
    
    test_categories = {
        "all_tests": {
            "command": base_cmd + ["tests/"],
            "description": "All tests (baseline)"
        },
        "unit_tests": {
            "command": base_cmd + ["tests/unit/"],
            "description": "Unit tests only"
        },
        "model_tests": {
            "command": base_cmd + ["tests/models/"],
            "description": "Model validation tests"
        },
        "end_to_end_tests": {
            "command": base_cmd + ["tests/end_to_end/", "-m", "live"],
            "description": "End-to-end tests with live marker"
        },
        "unit_and_models": {
            "command": base_cmd + ["tests/unit/", "tests/models/"],
            "description": "Unit and model tests combined"
        }
    }
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python_version": subprocess.run(["python", "--version"], capture_output=True, text=True).stdout.strip(),
            "pytest_version": subprocess.run(["uv", "run", "pytest", "--version"], capture_output=True, text=True).stdout.strip(),
            "cpu_count": os.cpu_count(),
            "working_directory": str(Path.cwd()),
        },
        "categories": {}
    }
    
    for category, config in test_categories.items():
        print(f"\n{'='*60}")
        print(f"Measuring: {config['description']}")
        print(f"{'='*60}")
        
        result = run_command(config["command"])
        result["description"] = config["description"]
        results["categories"][category] = result
        
        if result["success"]:
            print(f"✅ {category}: {result['duration']:.2f}s")
        else:
            print(f"❌ {category}: Failed ({result.get('error', 'Unknown error')})")
    
    return results


def save_results(results: Dict[str, Any], filename: str = None) -> str:
    """Save results to JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_performance_baseline_{timestamp}.json"
    
    # Create results directory
    results_dir = Path("test_performance_results")
    results_dir.mkdir(exist_ok=True)
    
    filepath = results_dir / filename
    
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    
    return str(filepath)


def print_summary(results: Dict[str, Any]) -> None:
    """Print a summary of the results."""
    print(f"\n{'='*80}")
    print("PERFORMANCE MEASUREMENT SUMMARY")
    print(f"{'='*80}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Python: {results['environment']['python_version']}")
    print(f"CPU Count: {results['environment']['cpu_count']}")
    print()
    
    # Sort by duration
    categories = [(name, data) for name, data in results["categories"].items()]
    categories.sort(key=lambda x: x[1]["duration"])
    
    print(f"{'Category':<20} {'Status':<10} {'Duration':<12} {'Description'}")
    print("-" * 80)
    
    for name, data in categories:
        status = "✅ PASS" if data["success"] else "❌ FAIL"
        duration = f"{data['duration']:.2f}s"
        print(f"{name:<20} {status:<10} {duration:<12} {data['description']}")
    
    # Calculate potential improvements
    print(f"\n{'='*80}")
    print("PARALLEL EXECUTION POTENTIAL")
    print(f"{'='*80}")
    
    unit_models_time = 0
    for category in ["unit_tests", "model_tests"]:
        if category in results["categories"] and results["categories"][category]["success"]:
            unit_models_time += results["categories"][category]["duration"]
    
    if unit_models_time > 0:
        estimated_parallel_time = unit_models_time / 4  # Assume 4x improvement
        print(f"Unit + Model tests current time: {unit_models_time:.2f}s")
        print(f"Estimated parallel time (4x): {estimated_parallel_time:.2f}s")
        print(f"Potential time savings: {unit_models_time - estimated_parallel_time:.2f}s")


def main():
    """Main function."""
    print("🚀 Starting test performance measurement...")
    print("This will run all test categories to establish baseline performance.")
    print("Note: This may take several minutes depending on your test suite size.\n")
    
    try:
        results = measure_test_categories()
        filepath = save_results(results)
        print_summary(results)
        
        print(f"\n📊 Results saved to: {filepath}")
        print("\n💡 Use this data to compare performance after implementing parallel execution.")
        
    except KeyboardInterrupt:
        print("\n🛑 Measurement interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Error during measurement: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())