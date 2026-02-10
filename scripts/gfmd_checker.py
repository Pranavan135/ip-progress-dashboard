import re
import requests
from typing import Optional


BASE_REPO = "nus-cs2103de-ay2526s2/duke"


# ---- GFMD patterns ----
GFMD_PATTERNS = [
    re.compile(r"^#{1,6}\s+.+", re.MULTILINE),          # heading
    re.compile(r"^[\*\-\+]\s+.+", re.MULTILINE),        # bullet list
    re.compile(r"^\d+\.\s+.+", re.MULTILINE),           # numbered list
    re.compile(r"```[a-zA-Z0-9_-]+\n[\s\S]*?\n```"),    # fenced code block w/ language
    re.compile(r"^-\s+\[( |x|X)\]\s+.+", re.MULTILINE), # task list
    re.compile(r":[a-zA-Z0-9_+\-]+:"),                  # emoji
    re.compile(r"^>\s+.+", re.MULTILINE),               # blockquote
    re.compile(r"\[[^\]]+\]\([^)]+\)"),                 # hyperlink
    re.compile(r"`[^`\n]+`"),                            # inline code
    re.compile(r"(\*\*.+?\*\*|\*[^*\n]+\*|~~.+?~~)")    # text formatting
]


def _parse_owner_repo(url: str) -> str:
    s = url.strip()
    if "github.com/" in s:
        s = s.split("github.com/", 1)[1]
    if s.endswith(".git"):
        s = s[:-4]
    s = s.strip("/")
    owner, repo = s.split("/", 1)
    return f"{owner}/{repo}"


def fork_pr_has_valid_gfmd(
        fork_url: str,
        github_token: Optional[str] = None
) -> bool:
    """
    Returns True iff there exists an OPEN PR in BASE_REPO
    whose head repo == fork_url AND whose PR body satisfies all GFMD rules.
    """

    fork_full = _parse_owner_repo(fork_url)

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "gfmd-checker"
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/repos/{BASE_REPO}/pulls",
            headers=headers,
            params={"state": "open", "per_page": 100, "page": page},
            timeout=20
        )
        r.raise_for_status()
        prs = r.json()
        if not prs:
            return False

        for pr in prs:
            head_repo = pr.get("head", {}).get("repo", {})
            if head_repo.get("full_name") != fork_full:
                continue

            body = pr.get("body") or ""
            if all(p.search(body) for p in GFMD_PATTERNS):
                return True

        page += 1
