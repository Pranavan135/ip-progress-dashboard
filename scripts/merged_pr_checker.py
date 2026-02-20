import re
import time
import requests

token_file = "tokens/github_token.txt"
with open(token_file, "r") as f:
    TOKEN = f.read().strip()
REPO_LIST_FILE = "repos.txt"

API = "https://api.github.com"

def normalize_repo(line: str) -> str | None:
    s = line.strip()
    if not s:
        return None

    # https://github.com/owner/repo(.git)?
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", s)
    if m:
        return f"{m.group(1)}/{m.group(2)}"

    # owner/repo
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", s):
        return s

    return None  # skip lines we don't understand

def has_merged_pr(owner_repo: str, token = TOKEN):
    q = f"repo:{owner_repo} is:pr is:merged"
    time.sleep(2)
    try:
        r = requests.get(
            f"{API}/search/issues",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            params={"q": q, "per_page": 1},
            timeout=15,
        )
        if r.status_code in (404, 403):
            print(f"ERROR {r.status_code} for {owner_repo}")
            return None
        r.raise_for_status()
        return r.json().get("total_count", 0) > 0
    except Exception:
        print(f"ERROR for {owner_repo}")
        return None

def main():
    with open(REPO_LIST_FILE) as f:
        for line in f:
            repo = normalize_repo(line)
            if not repo:
                print(f"Invalid format: {line.strip()}")
                continue

            merged = has_merged_pr(repo)
            if merged is True:
                print(f"{repo}: YES (has merged PR)")
            elif merged is False:
                print(f"{repo}: NO (no merged PRs)")
            else:
                print(f"{repo}: UNKNOWN / inaccessible")

            time.sleep(0.2)

if __name__ == "__main__":
    main()
