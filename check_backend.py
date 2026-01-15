
import os
import sys
import importlib
import pkgutil
import traceback

def check_backend_integrity():
    print(" Starting Backend Integrity Check...")
    
    # Add backend directory to path
    backend_path = os.path.join(os.getcwd(), 'backend')
    sys.path.append(backend_path)
    
    error_count = 0
    modules_checked = 0
    
    # Walk through modules directory
    modules_path = os.path.join(backend_path, 'modules')
    if not os.path.exists(modules_path):
        print(f" Modules directory not found at {modules_path}")
        return
    
    print(f" Scanning modules in {modules_path}...")
    
    for _, name, _ in pkgutil.iter_modules([modules_path]):
        modules_checked += 1
        module_name = f"modules.{name}"
        try:
            importlib.import_module(module_name)
            # print(f"   {module_name}")
        except Exception as e:
            error_count += 1
            print(f"   Error importing {module_name}:")
            print(f"     {str(e)}")
            # traceback.print_exc()
            
    # Check main.py
    print("\n Checking app/main.py...")
    try:
        import app.main
        print("   app.main imported successfully")
    except Exception as e:
        error_count += 1
        print(f"   Error importing app.main:")
        print(f"     {str(e)}")

    print(f"\n Summary: {modules_checked} modules checked, {error_count} errors found.")
    
    if error_count == 0:
        print(" Backend integrity check PASSED!")
    else:
        print(" Backend integrity check FAILED!")

if __name__ == "__main__":
    check_backend_integrity()
