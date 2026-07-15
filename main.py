import os
import sys
import platform
import subprocess
import importlib.util
import time
import glob

# ============================================
# DEVICE ARCHITECTURE CHECK
# ============================================

def check_device_architecture():
    print("\n" + "="*50)
    print("CHECKING DEVICE COMPATIBILITY")
    print("="*50)
    
    machine = platform.machine()
    print(f"[•] Machine architecture: {machine}")
    
    processor = platform.processor()
    print(f"[•] Processor: {processor}")
    
    is_64bits = sys.maxsize > 2**32
    print(f"[•] Python architecture: {'64-bit' if is_64bits else '32-bit'}")
    
    try:
        uname_output = subprocess.check_output(['uname', '-m'], text=True).strip()
        print(f"[•] Kernel architecture: {uname_output}")
        
        if uname_output in ['aarch64', 'arm64', 'x86_64', 'amd64']:
            print(f"[✓] Device is 64-bit ({uname_output})")
            return True, uname_output
        else:
            print(f"[✗] Device is 32-bit ({uname_output})")
            return False, uname_output
                
    except Exception:
        if is_64bits:
            return True, machine
        else:
            return False, machine

# ============================================
# DYNAMIC .SO CHECK
# ============================================

def check_compiled_module_compatibility():
    so_files = glob.glob("run*.so")
    
    if so_files:
        so_file = so_files[0]
        print(f"[•] Found compiled module: {so_file}")
        
        try:
            file_check = subprocess.check_output(['file', so_file], text=True)
            print(f"[•] Module info: {file_check.strip()}")
            
            if '64-bit' in file_check:
                print("[✓] Compiled module is 64-bit")
                return True
            elif '32-bit' in file_check:
                print("[!] Compiled module is 32-bit")
                return False
        except:
            print("[!] Could not analyze module")
    
    return None

# ============================================
# GIT PULL FUNCTION
# ============================================

def git_pull_updates():
    print("\n" + "="*50)
    print("CHECKING FOR UPDATES")
    print("="*50)
    
    if os.path.exists('.git'):
        try:
            subprocess.run(['git', 'fetch'], capture_output=True)
            status = subprocess.check_output(['git', 'status', '-uno'], text=True)
            
            if 'behind' in status:
                print("[!] Updates available!")
                choice = input("Pull updates? (y/n): ").lower()
                
                if choice == 'y':
                    subprocess.run(['git', 'pull'])
                    print("[✓] Updated!")
            else:
                print("[✓] Already up to date")
        except:
            print("[!] Git check failed")
    else:
        print("[!] Not a git repo")

# ============================================
# MODULE LOADING
# ============================================

def load_compiled_module():
    try:
        import run
        print("[✓] Loaded compiled module")
        return run, True
    except ImportError:
        try:
            if os.path.exists("run.py"):
                spec = importlib.util.spec_from_file_location("run", "run.py")
                run = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(run)
                print("[!] Running Python version")
                return run, False
            else:
                print("[✗] run module not found")
                return None, False
        except Exception as e:
            print(f"[✗] Load error: {e}")
            return None, False

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    os.system('clear')
    
    print("""
    
╔════════════════════════════════════════════════════════════╗
║           Yunick Facebook Tool - Cython Edition           ║
║                    Version 2.1                             ║
╚════════════════════════════════════════════════════════════╝
""")
    
    is_64bit, arch = check_device_architecture()
    
    if not is_64bit:
        print("\n[✗] 32-bit device not supported")
        input("Press Enter to exit...")
        sys.exit()
    
    print("\n[✓] Device OK")
    
    check_compiled_module_compatibility()
    
    git_pull_updates()
    
    base_path = "/sdcard" if 'ANDROID_ROOT' in os.environ else os.path.expanduser("~")
    
    dirs = [
        os.path.join(base_path, "Yunick"),
        os.path.join(base_path, "Yunick/logs"),
        os.path.join(base_path, "Yunick/accounts"),
        os.path.join(base_path, "Yunick/2fa")
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    print(f"[✓] Created folders in {base_path}/Yunick")
    
    run_module, compiled = load_compiled_module()
    
    if run_module is None:
        print("[✗] Cannot continue")
        sys.exit()
    
    print("\n[✓] Starting...\n")
    
    try:
        if hasattr(run_module, "method"):
            run_module.method()
        elif hasattr(run_module, "main"):
            run_module.main()
        elif hasattr(run_module, "auto"):
            run_module.auto()
        else:
            print("[!] No entry function found")
    except Exception as e:
        print(f"[✗] Runtime error: {e}")

if __name__ == "__main__":
    main()
