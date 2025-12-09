# coding=utf-8
"""
Main launcher for Bazarr application.
Handles subprocess management, restart/stop signals, and graceful shutdown.
"""

import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

from bazarr.app.get_args import args
from bazarr.literals import (
    EXIT_PYTHON_UPGRADE_NEEDED,
    EXIT_NORMAL,
    FILE_RESTART,
    FILE_STOP,
    ENV_RESTARTFILE,
    ENV_STOPFILE,
    EXIT_INTERRUPT,
)

# always flush print statements
sys.stdout.reconfigure(line_buffering=True)


def exit_program(status_code):
    print(f'Bazarr exited with status code {status_code}.')
    raise SystemExit(status_code)


def check_python_version():
    """Verify Python version meets requirements."""
    python_version = platform.python_version_tuple()
    minimum_py3_tuple = (3, 8, 0)
    minimum_py3_str = ".".join(str(i) for i in minimum_py3_tuple)

    if int(python_version[0]) < minimum_py3_tuple[0]:
        print("Python " + minimum_py3_str + " or greater required. "
              "Current version is " + platform.python_version() + ". Please upgrade Python.")
        exit_program(EXIT_PYTHON_UPGRADE_NEEDED)
    elif int(python_version[0]) == 3 and int(python_version[1]) > 12:
        print("Python version greater than 3.12.x is unsupported. Current version is " + platform.python_version() +
              ". Keep in mind that even if it works, you're on your own.")
    elif (int(python_version[0]) == minimum_py3_tuple[0] and int(python_version[1]) < minimum_py3_tuple[1]) or \
            (int(python_version[0]) != minimum_py3_tuple[0]):
        print("Python " + minimum_py3_str + " or greater required. "
              "Current version is " + platform.python_version() + ". Please upgrade Python.")
        exit_program(EXIT_PYTHON_UPGRADE_NEEDED)


def get_python_path():
    """Get the appropriate Python executable path."""
    if sys.platform == "darwin":
        # Do not run Python from within macOS framework bundle.
        python_bundle_path = os.path.join(sys.base_exec_prefix, "Resources", "Python.app", "Contents", "MacOS", "Python")
        if os.path.exists(python_bundle_path):
            import tempfile

            python_path = os.path.join(tempfile.mkdtemp(), "python")
            os.symlink(python_bundle_path, python_path)

            return python_path

    return sys.executable


def get_main_script_path():
    """Get the path to bazarr/main.py, handling both installed and development scenarios."""
    # Try to import and get the actual file location
    try:
        import bazarr.main
        bazarr_dir = os.path.dirname(os.path.dirname(bazarr.main.__file__))
        main_py = os.path.join(bazarr_dir, 'bazarr', 'main.py')
        if os.path.exists(main_py):
            return main_py
    except (ImportError, AttributeError):
        pass
    
    # Fallback: check relative to current script location
    dir_name = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(dir_name, 'main.py')
    if os.path.exists(main_py):
        return main_py
    
    # Last resort: assume development environment
    dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_py = os.path.join(dir_name, 'bazarr', 'main.py')
    return main_py


def start_bazarr(child_process=None):
    """Start the Bazarr application as a subprocess."""
    main_script = get_main_script_path()
    script = [get_python_path(), "-u", os.path.normcase(main_script)] + sys.argv[1:]
    ep = subprocess.Popen(script, stdout=None, stderr=None, stdin=subprocess.DEVNULL, env=os.environ)
    print(f"Bazarr starting child process with PID {ep.pid}...")
    return ep


def terminate_child(child_process):
    """Gracefully terminate the child process."""
    print(f"Terminating child process with PID {child_process.pid}")
    if child_process.poll() is None:   # Process is still running
        child_process.terminate()      # Send termination signal
    child_process.wait()               # Ensure it exits


def get_stop_status_code(input_file):
    """Read the stop status code from file."""
    try:
        with open(input_file, 'r') as file:
            # read status code from file, if it exists
            line = file.readline()
            try:
                status_code = int(line)
            except (ValueError, TypeError):
                status_code = EXIT_NORMAL
    except Exception:
        status_code = EXIT_NORMAL
    return status_code


def check_status(child_process, restart_file, stop_file):
    """Check for stop/restart signals and handle accordingly."""
    if os.path.exists(stop_file):
        status_code = get_stop_status_code(stop_file)
        try:
            print("Deleting stop file...")
            os.remove(stop_file)
        except Exception:
            print('Unable to delete stop file.')
        finally:
            terminate_child(child_process)
            exit_program(status_code)

    if os.path.exists(restart_file):
        try:
            print("Deleting restart file...")
            os.remove(restart_file)
        except Exception:
            print('Unable to delete restart file.')
        finally:
            terminate_child(child_process)
            print("Bazarr is restarting...")
            return start_bazarr(child_process)
    
    return child_process


def is_process_running(pid):
    """Check if a process with the given PID is still running."""
    commands = {
        "win": ["tasklist", "/FI", f"PID eq {pid}"],
        "linux": ["ps", "-eo", "pid"],
        "darwin": ["ps", "-ax", "-o", "pid"]
    }

    # Determine OS and execute corresponding command
    for key in commands:
        if sys.platform.startswith(key):
            result = subprocess.run(commands[key], capture_output=True, text=True)
            return str(pid) in result.stdout.split()

    print("Unsupported OS")
    return False


def interrupt_handler(signum, frame, child_process, interrupted):
    """Handle keyboard interrupt (Ctrl+C)."""
    # catch and ignore keyboard interrupt Ctrl-C
    # the child process Server object will catch SIGINT and perform an orderly shutdown
    if not interrupted[0]:
        # ignore user hammering Ctrl-C; we heard you the first time!
        interrupted[0] = True
        print('Handling keyboard interrupt...')
    else:
        if not is_process_running(child_process.pid):
            # this will be caught by the main loop below
            raise SystemExit(EXIT_INTERRUPT)


def main():
    """Main entry point for Bazarr launcher."""
    check_python_version()
    
    interrupted = [False]  # Use list to allow mutation in nested function
    
    def _interrupt_handler(signum, frame):
        interrupt_handler(signum, frame, child_process, interrupted)
    
    signal.signal(signal.SIGINT, _interrupt_handler)
    
    restart_file = os.path.join(args.config_dir, FILE_RESTART)
    stop_file = os.path.join(args.config_dir, FILE_STOP)
    os.environ[ENV_STOPFILE] = stop_file
    os.environ[ENV_RESTARTFILE] = restart_file

    # Cleanup leftover files
    try:
        os.remove(restart_file)
    except FileNotFoundError:
        pass

    try:
        os.remove(stop_file)
    except FileNotFoundError:
        pass

    # Initial start of main bazarr process
    child_process = start_bazarr()

    # Keep the script running forever until stop is requested through term, special files or keyboard interrupt
    while True:
        child_process = check_status(child_process, restart_file, stop_file)
        try:
            time.sleep(5)
        except (KeyboardInterrupt, SystemExit, ChildProcessError):
            # this code should never be reached, if signal handling is working properly
            print('Bazarr exited main script file via keyboard interrupt.')
            exit_program(EXIT_INTERRUPT)


if __name__ == '__main__':
    sys.exit(main())
