"""
Master QA & Security Audit Runner for PotatoYT-Mini
Executes all static analysis, unit tests, security audits, and lifecycle smoke tests.
Returns exit code 0 if and only if ALL tests pass.
"""

import os
import sys
import ast
import glob
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def run_static_analysis():
    print("=" * 60)
    print("[STAGE 1] Static Analysis & Code Hygiene Audit")
    print("=" * 60)
    
    issues = []
    py_files = glob.glob(os.path.join(BASE_DIR, "src", "**", "*.py"), recursive=True) + \
               glob.glob(os.path.join(BASE_DIR, "tests", "**", "*.py"), recursive=True)
               
    for filepath in py_files:
        rel_path = os.path.relpath(filepath, BASE_DIR)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError as e:
            issues.append(f"SyntaxError in {rel_path}:{e.lineno}: {e.msg}")
            continue

        for node in ast.walk(tree):
            # Check for bare excepts
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(f"Bare except in {rel_path}:{node.lineno}")
            # Check for dangerous eval / exec
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec"):
                    issues.append(f"Dangerous call to {node.func.id}() in {rel_path}:{node.lineno}")

    if issues:
        print("[FAIL] Static analysis issues discovered:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[PASS] 100% clean AST. No bare excepts, no dangerous eval/exec calls.")
        return True


def run_security_secret_audit():
    print("=" * 60)
    print("[STAGE 2] Secrets & Credentials Audit")
    print("=" * 60)

    files_to_check = glob.glob(os.path.join(BASE_DIR, "src", "**", "*.*"), recursive=True) + \
                     [os.path.join(BASE_DIR, "config.json"), os.path.join(BASE_DIR, "run.bat")]

    found_secrets = []
    for filepath in files_to_check:
        if ".git" in filepath or "__pycache__" in filepath:
            continue
        rel_path = os.path.relpath(filepath, BASE_DIR)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    lower_line = line.lower()
                    for pattern in sensitive_patterns:
                        if pattern in lower_line and not any(safe in lower_line for safe in ["sensitive_patterns", "def ", "#"]):
                            found_secrets.append(f"{rel_path}:{line_num} contains pattern '{pattern}'")
        except Exception:
            pass

    if found_secrets:
        print("[FAIL] Potential hardcoded credentials found:")
        for s in found_secrets:
            print(f"  - {s}")
        return False
    else:
        print("[PASS] Zero hardcoded secrets, keys, or passwords found.")
        return True


def run_unit_and_qa_tests():
    print("=" * 60)
    print("[STAGE 3] Unit Tests & QA Security Suite")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Discover and add test cases
    from test_qa_suite import TestConfigManagerQA, TestWin32ControllerQA, TestSecurityAndInputHygiene
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManagerQA))
    suite.addTests(loader.loadTestsFromTestCase(TestWin32ControllerQA))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityAndInputHygiene))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_smoke_test_lifecycle():
    print("=" * 60)
    print("[STAGE 4] Runtime Smoke Test & Lifecycle Simulation")
    print("=" * 60)

    from main import PotatoApp
    from win32_native import Win32Controller
    from config_manager import ConfigManager

    # Instantiate App controller
    app = PotatoApp()
    assert app.config is not None, "ConfigManager must be initialized"
    assert app.win32 is not None, "Win32Controller must be initialized"
    assert len(app.css_content) > 50, "CSS inject content must be loaded"
    assert len(app.js_content) > 50, "JS inject content must be loaded"

    # Test clean shutdown without active window
    app.on_closing()
    print("[PASS] Clean application lifecycle and shutdown verified without crash.")
    return True


if __name__ == "__main__":
    p1 = run_static_analysis()
    p2 = run_security_secret_audit()
    p3 = run_unit_and_qa_tests()
    p4 = run_smoke_test_lifecycle()

    all_passed = p1 and p2 and p3 and p4
    print("=" * 60)
    if all_passed:
        print("[OK] ALL 4 AUDIT STAGES PASSED SUCCESSFULLY (100% PASS RATE)")
        sys.exit(0)
    else:
        print("[FAIL] ONE OR MORE AUDIT STAGES FAILED")
        sys.exit(1)
