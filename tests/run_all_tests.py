import subprocess
import os
import sys
import time

# List of all test files discovered
test_files = [
    "test_json_robustness.py",
    "tests/test_ai_render.py",
    "tests/test_all_exports.py",
    "tests/test_clipart_size.py",
    "test_fonts.py",
    "test_e2e_navigation.py",
    "test_regex.py",
    "test_cpp_templates_v2.py",
    "test_render.py",
    "test_user_payload.py",
    "test_cpp_templates.py",
    "test_hybrid.py",
    "test_robust_regex.py",
    "test_user_payload_render.py"
]

def run_test(file_path):
    print(f"\n--- Running: {file_path} ---")
    try:
        # We use a fresh environment for each test
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}"
        
        # Run as a separate process to avoid conflicts
        result = subprocess.run(
            [sys.executable, file_path],
            env=env,
            capture_output=True,
            text=True,
            timeout=180 # 3 min timeout per test
        )
        
        if result.returncode == 0:
            print(f"✅ {file_path} PASSED")
            return True, ""
        else:
            print(f"❌ {file_path} FAILED (Exit Code: {result.returncode})")
            return False, result.stdout + "\n" + result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {file_path} TIMED OUT")
        return False, "TIMEOUT: Took more than 180s"
    except Exception as e:
        print(f"☢️ {file_path} ERROR: {e}")
        return False, str(e)

def main():
    print("══════════════════════════════════════════════════════════")
    print("   TEXTPRISM MASTER TEST RUNNER")
    print("══════════════════════════════════════════════════════════")
    
    passed = []
    failed = []
    
    # Ensure dependencies are available
    # playwright install might be needed but assuming it's already there since I ran it before
    
    for test in test_files:
        if not os.path.exists(test):
            print(f"⚠️  Skipping {test} (File not found)")
            continue
            
        success, error_msg = run_test(test)
        if success:
            passed.append(test)
        else:
            failed.append((test, error_msg))
        
        # Give system a moment to breathe between tests
        time.sleep(2)

    print("\n" + "═"*60)
    print(f"TEST SUMMARY: {len(passed)} PASSED, {len(failed)} FAILED")
    print("═"*60)
    
    if passed:
        print("\n✅ PASSED TESTS:")
        for t in passed: print(f" - {t}")
        
    if failed:
        print("\n❌ FAILED TESTS:")
        for t, err in failed:
            print(f" - {t}")
            # print(f"   Error: {err.splitlines()[-5:] if err else 'No output'}") # last 5 lines

    if not failed:
        print("\n✨ ALL CORE SYSTEMS ARE STABLE ✨")
        sys.exit(0)
    else:
        print("\n☢️  SOME SYSTEMS ARE UNSTABLE ☢️")
        sys.exit(1)

if __name__ == "__main__":
    main()
