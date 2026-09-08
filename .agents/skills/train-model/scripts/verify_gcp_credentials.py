#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys

def check_gcloud() -> tuple[bool, str]:
    candidate_bins = [
        shutil.which("gcloud"),
        os.path.expanduser("~/google-cloud-sdk/bin/gcloud"),
        "/usr/local/bin/gcloud",
        "/opt/homebrew/bin/gcloud",
    ]
    gcloud_bin = next((b for b in candidate_bins if b and os.path.exists(b)), None)
    if not gcloud_bin:
        return False, "gcloud CLI not found in PATH or ~/google-cloud-sdk/bin"
    try:
        env = os.environ.copy()
        if "CLOUDSDK_PYTHON" not in env:
            env["CLOUDSDK_PYTHON"] = sys.executable
        res = subprocess.run([gcloud_bin, "config", "get-value", "project"], capture_output=True, text=True, timeout=5, env=env)
        project = res.stdout.strip()
        if res.returncode == 0 and project and project != "(unset)":
            return True, f"Active project: {project}"
        return False, "gcloud present but project is unset"
    except Exception as e:
        return False, str(e)

def check_google_auth() -> tuple[bool, str]:
    try:
        import google.auth
        credentials, project = google.auth.default()
        return True, f"ADC authenticated (project: {project})"
    except Exception as e:
        return False, f"ADC not configured: {e}"

def main():
    gcloud_ok, gcloud_msg = check_gcloud()
    auth_ok, auth_msg = check_google_auth()

    status = {
        "gcloud": {"valid": gcloud_ok, "detail": gcloud_msg},
        "google_auth_adc": {"valid": auth_ok, "detail": auth_msg},
    }
    print(json.dumps(status, indent=2))
    
    # Ready if either gcloud CLI or google-auth ADC is present
    if gcloud_ok or auth_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
