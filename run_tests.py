#!/usr/bin/env python3
"""Simple test runner for Kiddy Backend."""

import sys
import subprocess
from pathlib import Path

def main():
    """Run all tests."""
    print("Running Kiddy Backend tests...")
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("All tests passed!")
            print(result.stdout)
        else:
            print("Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return 1
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 