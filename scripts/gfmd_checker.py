import re
import requests
from typing import Optional, List

BASE_REPO = "nus-cs2103de-ay2526s2/duke"

# ---- GFMD patterns ----
# Improvements:
# 1) bullets: allow '•' (\u2022) as well
# 2) emoji: allow :shortcode: OR common unicode emoji ranges
GFMD_PATTERNS = [
    re.compile(r"^#{1,6}\s+.+", re.MULTILINE),                 # heading
#     re.compile(r"^[\*\-\+\u2022]\s+.+", re.MULTILINE),         # bullet list (- * + •)
#     re.compile(r"^\d+\.\s+.+", re.MULTILINE),                  # numbered list
    re.compile(r"```[a-zA-Z0-9_-]+\n[\s\S]*?\n```"),           # fenced code block w/ language
    re.compile(r"^-\s+\[( |x|X)\]\s+.+", re.MULTILINE),        # task list
#     re.compile(r":[a-zA-Z0-9_+\-]+:|[\U0001F300-\U0001FAFF]"), # emoji (:rocket: or 🚀)
    re.compile(r"^>\s+.+", re.MULTILINE),                      # blockquote
    re.compile(r"\[[^\]]+\]\([^)]+\)"),                        # hyperlink
    re.compile(r"`[^`\n]+`"),                                   # inline code
    re.compile(r"(\*\*.+?\*\*|\*[^*\n]+\*|~~.+?~~)")           # text formatting
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

def _gh_get(url: str, headers: dict, params: dict, timeout: int = 20):
    r = requests.get(url, headers=headers, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def _collect_issue_comments(pr_number: int, headers: dict) -> List[str]:
    # PR "conversation" comments are issue comments:
    # GET /repos/{owner}/{repo}/issues/{issue_number}/comments
    texts = []
    page = 1
    while True:
        data = _gh_get(
            f"https://api.github.com/repos/{BASE_REPO}/issues/{pr_number}/comments",
            headers=headers,
            params={"per_page": 100, "page": page},
        )
        if not data:
            break
        texts.extend([(c.get("body") or "") for c in data])
        page += 1
    return texts

def _collect_review_comments(pr_number: int, headers: dict) -> List[str]:
    # Inline diff comments (review comments):
    # GET /repos/{owner}/{repo}/pulls/{pull_number}/comments
    texts = []
    page = 1
    while True:
        data = _gh_get(
            f"https://api.github.com/repos/{BASE_REPO}/pulls/{pr_number}/comments",
            headers=headers,
            params={"per_page": 100, "page": page},
        )
        if not data:
            break
        texts.extend([(c.get("body") or "") for c in data])
        page += 1
    return texts

def fork_pr_has_valid_gfmd_in_body_or_comments(
        fork_url: str,
        github_token: Optional[str] = None
) -> bool:
    """
    Returns True iff there exists an OPEN PR in BASE_REPO
    whose head repo == fork_url AND the combined text from:
      - PR body
      - issue comments (conversation comments)
      - review comments (inline comments)
    satisfies all GFMD rules.
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
        prs = _gh_get(
            f"https://api.github.com/repos/{BASE_REPO}/pulls",
            headers=headers,
            params={"state": "open", "per_page": 100, "page": page},
        )
        if not prs:
            return False

        for pr in prs:
            head_repo = pr.get("head", {}).get("repo", {})
            if head_repo.get("full_name") != fork_full:
                continue

            pr_number = pr.get("number")
            pr_body = pr.get("body") or ""

            # Collect comments
            issue_comments = _collect_issue_comments(pr_number, headers)
            review_comments = _collect_review_comments(pr_number, headers)

            combined = "\n\n".join([pr_body, *issue_comments, *review_comments])

            if all(p.search(combined) for p in GFMD_PATTERNS):
                return True

        page += 1
