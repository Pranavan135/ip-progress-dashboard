import write_to_csv as wv
import pandas as pd
import requests

def parse_owner_repo(repo_url: str) -> tuple[str, str]:
    clean = repo_url.strip().replace(".git", "")
    parts = clean.split("/")
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo

def has_released_jar(repo_url: str, headers) -> bool:
    """
    Returns True if the repo has a GitHub Release containing an asset ending with .jar
    Returns False otherwise. Never raises (won't crash).
    """
    try:
        owner, repo = parse_owner_repo(repo_url)

        # Try latest release first (fast path)
        latest_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        r = requests.get(latest_url, headers=headers, timeout=15)

        if r.status_code == 200:
            data = r.json()
            assets = data.get("assets", [])
            return any(a.get("name", "").lower().endswith(".jar") for a in assets)

        # If no "latest" (often 404 when no releases), optionally check all releases
        if r.status_code == 404:
            all_url = f"https://api.github.com/repos/{owner}/{repo}/releases?per_page=20"
            r2 = requests.get(all_url, headers=headers, timeout=15)
            if r2.status_code != 200:
                return False

            releases = r2.json()
            for rel in releases:
                for a in rel.get("assets", []):
                    if a.get("name", "").lower().endswith(".jar"):
                        return True
            return False

        # Other statuses (401/403/5xx etc.) => treat as "no"
        return False

    except Exception:
        return False


def has_file(repo_url, headers, file_name="Ui.png"):
    try:
        parts = repo_url.replace(".git", "").split("/")
        owner = parts[-2]
        repo = parts[-1]

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/docs/" + file_name

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            return False

    except Exception as e:
        print(f"Error checking {repo_url}: {e}")
        return False

if __name__ == "__main__":
    repo = "nus-cs2103de-ay2526s2/duke"

    users = wv.read_csv("data/name_repo.csv")
    df = pd.read_csv("data/student_progress.csv", dtype=str)
    token_file = "tokens/github_token.txt"
    with open(token_file, "r") as f:
        token = f.read().strip()

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    for i in range(len(users)):
        if has_file(users[i][1], headers, file_name="Ui.png"):
            df.loc[df["Full Name"] == users[i][0], "Ui.png"] = '1'
        if has_file(users[i][1], headers, file_name="README.md"):
            df.loc[df["Full Name"] == users[i][0], "Published UG"] = '1'
        if has_released_jar(users[i][1], headers):
            df.loc[df["Full Name"] == users[i][0], "JAR released"] = '1'

    df.to_csv("data/student_progress.csv", index=False)