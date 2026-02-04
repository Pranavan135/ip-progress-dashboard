import requests
from urllib.parse import urlparse

def parse_github_url(repo_url: str):
    repo_url = repo_url.strip()
    parsed = urlparse(repo_url)

    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]  # remove trailing ".git" only

    parts = path.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url!r}")

    return parts[0], parts[1]

def get_all_tags_from_url(repo_url, token=None):
    owner, repo = parse_github_url(repo_url)

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "tag-fetcher/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    tags = []
    page = 1
    per_page = 100

    while True:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        resp = requests.get(api_url, headers=headers, params={"per_page": per_page, "page": page}, timeout=20)

        if resp.status_code != 200:
            print(f"ERROR {resp.status_code} for {owner}/{repo}")
            print(resp.text[:300])
            print("X-RateLimit-Remaining:", resp.headers.get("X-RateLimit-Remaining"))
            return []

        data = resp.json()
        if not data:
            break

        tags.extend(t["name"] for t in data)
        page += 1

    return tags

def check_auth(token):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "tag-fetcher/1.0",
        "Authorization": f"Bearer {token}",
    }
    r = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=20)
    print("status:", r.status_code)
    print("limit:", r.headers.get("X-RateLimit-Limit"))
    print("remaining:", r.headers.get("X-RateLimit-Remaining"))
    print("reset:", r.headers.get("X-RateLimit-Reset"))
    print("body message:", r.json().get("message"))
