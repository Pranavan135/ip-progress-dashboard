import subprocess
import write_to_csv as wv
import pandas as pd
import merged_pr_checker as mpc

def branch_exists(repo_url: str, branch: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repo_url, branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        return result.stdout.strip() != ""
    except Exception:
        return False

import requests

def parse_github_full_name(repo_url_or_fullname: str) -> str:
    s = repo_url_or_fullname.strip()

    # If it's a URL: https://github.com/OWNER/REPO(.git)
    if "github.com/" in s:
        s = s.split("github.com/", 1)[1]

    # drop possible suffixes/fragments
    s = s.split("#", 1)[0].split("?", 1)[0]
    if s.endswith(".git"):
        s = s[:-4]
    s = s.strip("/")

    # now should be OWNER/REPO
    return s

def repo_made_pr_safe(fork_repo_url: str, target_repo: str, token: str | None = None) -> bool:
    fork_repo = parse_github_full_name(fork_repo_url)
    target = parse_github_full_name(target_repo)

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"

    page = 1
    while True:
        try:
            r = requests.get(
                f"https://api.github.com/repos/{target}/pulls",
                headers=headers,
                params={"state": "open", "per_page": 100, "page": page},
                timeout=15
            )

            if r.status_code != 200:
                return False

            prs = r.json()
            if not prs:
                return False

            for pr in prs:
                head_repo = pr.get("head", {}).get("repo", {})
                if head_repo.get("full_name") == fork_repo:
                    return True

            page += 1

        except requests.RequestException:
            return False


if __name__ == "__main__":
    repo = "nus-cs2103de-ay2526s2/duke"
    branches = ["branch-A-Assertions", "branch-A-CodeQuality"]

    users = wv.read_csv("data/name_repo.csv")
    df = pd.read_csv("data/student_progress.csv", dtype=str)
    token_file = "tokens/github_token.txt"
    with open(token_file, "r") as f:
        token = f.read().strip()
    headers = df.columns.tolist()

    for i in range(len(users)):
        for j in range(len(branches)):
            if branch_exists(users[i][1], branches[j]):
                df.loc[df["Full Name"] == users[i][0], branches[j]] = '1'

            if mpc.has_merged_pr(mpc.normalize_repo(users[i][1]), token):
                df.loc[df["Full Name"] == users[i][0], "Merging PRs"] = '1'


    df.to_csv("data/student_progress.csv", index=False)
