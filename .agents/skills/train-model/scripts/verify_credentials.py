import os
import sys
import json
import urllib.request
import base64
import netrc
import subprocess

def check_modal() -> tuple[bool, str]:
    try:
        res = subprocess.run(
            ["uv", "run", "--with", "modal", "modal", "profile", "current"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0 and res.stdout.strip():
            return True, res.stdout.strip()
        return False, res.stderr.strip() or "Modal not authenticated"
    except Exception as e:
        return False, str(e)

def check_hf(token: str | None) -> tuple[bool, str]:
    if not token:
        return False, "HF_TOKEN not set"
    req = urllib.request.Request(
        "https://huggingface.co/api/whoami-v2",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return True, data.get("name", "Authenticated")
    except Exception as e:
        return False, str(e)

def check_wandb(key: str | None) -> tuple[bool, str]:
    if not key:
        netrc_path = os.path.expanduser("~/.netrc")
        if os.path.exists(netrc_path):
            try:
                auth = netrc.netrc(netrc_path).authenticators("api.wandb.ai")
                if auth:
                    key = auth[2]
            except Exception:
                pass

    if not key:
        return False, "WANDB_API_KEY not set"

    auth_header = "Basic " + base64.b64encode(f"api:{key}".encode()).decode()
    req = urllib.request.Request(
        "https://api.wandb.ai/graphql",
        data=json.dumps({"query": "query { viewer { username email } }"}).encode(),
        headers={"Authorization": auth_header, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            viewer = data.get("data", {}).get("viewer")
            if viewer and viewer.get("username"):
                return True, viewer.get("username")
            return False, "Invalid credentials returned by API"
    except Exception as e:
        return False, str(e)

def main():
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    wandb_key = os.environ.get("WANDB_API_KEY")

    modal_ok, modal_msg = check_modal()
    hf_ok, hf_msg = check_hf(hf_token)
    wandb_ok, wandb_msg = check_wandb(wandb_key)

    results = {
        "modal": {"valid": modal_ok, "detail": modal_msg},
        "huggingface": {"valid": hf_ok, "detail": hf_msg},
        "wandb": {"valid": wandb_ok, "detail": wandb_msg},
    }
    print(json.dumps(results, indent=2))

    if not (modal_ok and hf_ok and wandb_ok):
        sys.exit(1)

if __name__ == "__main__":
    main()
