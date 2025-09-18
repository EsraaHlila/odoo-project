import subprocess
import logging
import os
from odoo import models

_logger = logging.getLogger(__name__)

class SyncRunner(models.Model):
    _name = "sync.runner"
    _description = "Runner for Node.js Sync Scripts"

    def run_all_scripts(self):
        """Run all Node.js scripts via subprocess"""
        module_dir = os.path.dirname(os.path.abspath(__file__))  # models/
        scripts_dir = os.path.join(module_dir, "..", "scripts")  # module_root/scripts

        scripts = {
            "db2": [
                os.path.join(scripts_dir, "sync_child.js"),
                os.path.join(scripts_dir, "sync_par.js"),
                os.path.join(scripts_dir, "sync_leads.js"),
                os.path.join(scripts_dir, "sync_pack.js"),
                os.path.join(scripts_dir, "sync_pay.js"),
                os.path.join(scripts_dir, "sync_sub.js"),
            ]
        }

        for db, script_list in scripts.items():
            for script in script_list:
                if not os.path.exists(script):
                    _logger.error(f"Script not found: {script}")
                    continue
                try:
                    _logger.info(f"Running sync script for {db}: {script}")
                    result = subprocess.run(
                        ["node", script],
                        cwd=scripts_dir,  # <- important: Node will use this as the working dir
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    _logger.info(f"Output ({script}): {result.stdout}")
                    if result.stderr:
                        _logger.warning(f"Errors ({script}): {result.stderr}")
                except subprocess.CalledProcessError as e:
                    _logger.error(f"Failed running {script}: {e.stderr}")
