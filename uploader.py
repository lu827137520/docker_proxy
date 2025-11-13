#!/usr/bin/env python3
import sys
import json
import subprocess

def sync_image(source: str, target: str):
    """拉取源镜像，打标签，推送到目标仓库"""
    print(f"  📥 Pulling {source}...")
    subprocess.run(["docker", "pull", source], check=True)

    print(f"  🏷️  Tagging as {target}...")
    subprocess.run(["docker", "tag", source, target], check=True)

    print(f"  📤 Pushing {target}...")
    subprocess.run(["docker", "push", target], check=True)

def docker_login(registry: str, username: str, password: str):
    """使用 --password-stdin 安全登录 Docker Registry"""
    print(f"🔑 Logging in to {registry}...")
    proc = subprocess.Popen(
        ["docker", "login", registry, "-u", username, "--password-stdin"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    stdout, _ = proc.communicate(input=password)
    if proc.returncode != 0:
        print("❌ Docker login failed:", file=sys.stderr)
        print(stdout, file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Usage: python uploader.py <username> <password> <registry_url>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    registry_url = sys.argv[3]

    # 安全登录
    docker_login(registry_url, username, password)

    try:
        # 读取并验证 images.json
        with open('images.json') as f:
            images = json.load(f)

        if not isinstance(images, list):
            raise ValueError("images.json must be a JSON array")

        for img in images:
            if not (isinstance(img, dict) and "source" in img and "target" in img):
                raise ValueError(f"Invalid image entry: {img}")
            print(f"\n🔄 Syncing: {img['source']} → {img['target']}")
            sync_image(img["source"], img["target"])

        print("\n✅ All images synced successfully!")

    except Exception as e:
        print(f"💥 Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # 登出（即使出错也尝试登出）
        subprocess.run(["docker", "logout", registry_url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
