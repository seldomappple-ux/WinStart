import subprocess
import os
import time
import threading
from typing import List, Dict

class Launcher:
    @staticmethod
    def launch_group(items: List[Dict]):
        """
        Launch a list of items in a separate thread to avoid freezing UI.
        """
        threading.Thread(target=Launcher._launch_items_thread, args=(items,), daemon=True).start()

    @staticmethod
    def _launch_items_thread(items: List[Dict]):
        for item in items:
            path = item.get("path")
            args = item.get("args", "")
            delay = item.get("delay", 0)

            if delay > 0:
                time.sleep(delay)

            if path and os.path.exists(path):
                try:
                    # Construct command
                    if args:
                        cmd = [path]
                        # Simple split, might need shlex for complex args but keeping it simple for Windows
                        cmd.extend(args.split())
                        
                        working_dir = os.path.dirname(path)
                        subprocess.Popen(cmd, cwd=working_dir, shell=False)
                    else:
                        # Use os.startfile for better compatibility (like double-clicking)
                        os.startfile(path)
                    
                except Exception as e:
                    print(f"Failed to launch {path}: {e}")
            else:
                print(f"Path not found: {path}")
