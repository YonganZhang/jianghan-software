import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    try:
        import PyInstaller
        print("PyInstaller found.")
        return True
    except ImportError:
        print("PyInstaller NOT found in the current environment.")
        print("Please run: pip install pyinstaller")
        return False

def build():
    if not check_pyinstaller():
        return

    work_dir = os.path.dirname(os.path.abspath(__file__))
    spec_file = os.path.join(work_dir, 'backend.spec')
    
    if not os.path.exists(spec_file):
        print(f"Spec file not found: {spec_file}")
        return

    print(f"Building backend from: {spec_file}")
    
    # Clean previous build
    dist_dir = os.path.join(work_dir, 'dist')
    build_dir = os.path.join(work_dir, 'build')
    if os.path.exists(dist_dir):
        print("Cleaning dist directory...")
        # shutil.rmtree(dist_dir) # Optional: Be careful deleting
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        spec_file
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=work_dir)
    
    print("\nBuild completed successfully!")
    print(f"Executable is in: {os.path.join(dist_dir, 'backend')}")

if __name__ == '__main__':
    build()
