#!/usr/bin/env python3
# run_tests.py - Comprehensive test runner with various options

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"ERROR: Command not found. Please ensure the required tools are installed.")
        return False

def install_test_dependencies():
    """Install test dependencies"""
    print("Installing test dependencies...")
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"],
        "Installing test dependencies"
    )

def run_unit_tests(verbose=False, coverage=True, markers=None):
    """Run unit tests"""
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing", "--cov-report=html"])
    
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])
    
    cmd.append("tests/")
    
    return run_command(cmd, "Running unit tests")

def run_linting():
    """Run code linting"""
    success = True
    
    # Flake8
    if not run_command(
        [sys.executable, "-m", "flake8", "--max-line-length=100", "--exclude=tests/", "."],
        "Running flake8 linting"
    ):
        success = False
    
    # Check if black is available and run it
    try:
        subprocess.run([sys.executable, "-m", "black", "--version"], 
                      check=True, capture_output=True)
        if not run_command(
            [sys.executable, "-m", "black", "--check", "--diff", "."],
            "Checking code formatting with black"
        ):
            print("Note: Run 'python -m black .' to auto-format code")
            success = False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Black not available, skipping format check")
    
    return success

def run_type_checking():
    """Run type checking with mypy"""
    try:
        subprocess.run([sys.executable, "-m", "mypy", "--version"], 
                      check=True, capture_output=True)
        return run_command(
            [sys.executable, "-m", "mypy", "--ignore-missing-imports", "."],
            "Running type checking with mypy"
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("MyPy not available, skipping type checking")
        return True

def run_security_checks():
    """Run security checks"""
    try:
        subprocess.run([sys.executable, "-m", "bandit", "--version"], 
                      check=True, capture_output=True)
        return run_command(
            [sys.executable, "-m", "bandit", "-r", ".", "-x", "tests/"],
            "Running security checks with bandit"
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Bandit not available, skipping security checks")
        return True

def generate_test_report():
    """Generate comprehensive test report"""
    report_file = "test_report.txt"
    
    print(f"\nGenerating test report: {report_file}")
    
    with open(report_file, 'w') as f:
        f.write("AI Tool Intelligence Platform - Test Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {os.popen('date').read()}")
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Working Directory: {os.getcwd()}\n\n")
        
        # Test structure info
        f.write("Test Structure:\n")
        f.write("-" * 20 + "\n")
        
        test_files = list(Path("tests").glob("test_*.py"))
        f.write(f"Total test files: {len(test_files)}\n")
        
        for test_file in test_files:
            f.write(f"  - {test_file.name}\n")
        
        f.write("\n")
        
        # Coverage info (if available)
        if os.path.exists("htmlcov/index.html"):
            f.write("Coverage report available at: htmlcov/index.html\n\n")
        
        f.write("Test Categories:\n")
        f.write("-" * 20 + "\n")
        f.write("- Unit tests: Fast tests with no external dependencies\n")
        f.write("- Integration tests: Tests that may require external services\n")
        f.write("- API tests: Tests requiring API access\n")
        f.write("- Network tests: Tests requiring network connectivity\n\n")
        
        f.write("Available Test Commands:\n")
        f.write("-" * 25 + "\n")
        f.write("python run_tests.py --unit          # Run unit tests only\n")
        f.write("python run_tests.py --integration   # Run integration tests\n")
        f.write("python run_tests.py --api          # Run API tests\n")
        f.write("python run_tests.py --all          # Run all tests\n")
        f.write("python run_tests.py --lint         # Run linting only\n")
        f.write("python run_tests.py --type-check   # Run type checking\n")
        f.write("python run_tests.py --security     # Run security checks\n")
    
    print(f"Test report generated: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="AI Tool Intelligence Platform Test Runner")
    
    # Test type selection
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--network", action="store_true", help="Run network tests")
    parser.add_argument("--slow", action="store_true", help="Include slow tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Quality checks
    parser.add_argument("--lint", action="store_true", help="Run linting")
    parser.add_argument("--type-check", action="store_true", help="Run type checking")
    parser.add_argument("--security", action="store_true", help="Run security checks")
    parser.add_argument("--quality", action="store_true", help="Run all quality checks")
    
    # Options
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--ci", action="store_true", help="CI mode (all checks, strict)")
    
    args = parser.parse_args()
    
    # Ensure we're in the backend directory
    if not os.path.exists("tests"):
        print("Error: tests directory not found. Please run from backend directory.")
        sys.exit(1)
    
    success = True
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            print("Failed to install dependencies")
            sys.exit(1)
    
    # Determine what to run
    if args.ci:
        # CI mode: run everything
        print("Running in CI mode - all checks enabled")
        
        if not run_linting():
            success = False
        
        if not run_type_checking():
            success = False
        
        if not run_security_checks():
            success = False
        
        if not run_unit_tests(verbose=True, coverage=not args.no_coverage):
            success = False
    
    elif args.quality:
        # Quality checks only
        if args.lint or args.quality:
            if not run_linting():
                success = False
        
        if args.type_check or args.quality:
            if not run_type_checking():
                success = False
        
        if args.security or args.quality:
            if not run_security_checks():
                success = False
    
    else:
        # Individual quality checks
        if args.lint:
            if not run_linting():
                success = False
        
        if args.type_check:
            if not run_type_checking():
                success = False
        
        if args.security:
            if not run_security_checks():
                success = False
        
        # Test execution
        if args.unit or args.integration or args.api or args.network or args.slow or args.all:
            markers = []
            
            if args.unit:
                markers.append("unit")
            if args.integration:
                markers.append("integration")
            if args.api:
                markers.append("api")
            if args.network:
                markers.append("network")
            if args.slow:
                markers.append("slow")
            
            # If no specific markers and not --all, default to unit tests
            if not markers and not args.all:
                markers = ["unit"]
            
            if not run_unit_tests(
                verbose=args.verbose, 
                coverage=not args.no_coverage,
                markers=markers if not args.all else None
            ):
                success = False
        
        # If no specific arguments, run default test suite
        elif not any([args.lint, args.type_check, args.security, args.quality]):
            print("No specific tests requested, running default unit tests...")
            if not run_unit_tests(verbose=args.verbose, coverage=not args.no_coverage, markers=["unit"]):
                success = False
    
    # Generate report if requested
    if args.report:
        generate_test_report()
    
    # Exit with appropriate code
    if success:
        print("\n" + "="*60)
        print("✅ All checks passed!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ Some checks failed!")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()