"""Fetch profile statistics from GitHub and reduce them to what the panels draw."""

import json
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import date

GRAPHQL_URL = "https://api.github.com/graphql"

# Notebook outputs and markup dwarf real code when measured in bytes, and build
# files are generated, so none of them say anything about what was written.
EXCLUDED_LANGUAGES = frozenset(
    {"Jupyter Notebook", "HTML", "CSS", "SCSS", "CMake", "Makefile", "Dockerfile", "Batchfile"}
)
# Below this share of all code, a language is project scaffolding, not one in use.
MIN_LANGUAGE_SHARE = 0.01

_QUERY = """
query ($cursor: String) {
  viewer {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class Language:
    name: str
    share: float


@dataclass(frozen=True)
class Stats:
    total_contributions: int
    days: tuple[tuple[date, int], ...]
    repositories: int
    languages: tuple[Language, ...]

    @property
    def busiest_day(self) -> int:
        return max((count for _, count in self.days), default=0)


def _request(token: str, cursor: str | None) -> dict:
    body = json.dumps({"query": _QUERY, "variables": {"cursor": cursor}}).encode()
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-stats-panels",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(f"GitHub API error: {payload['errors']}")
    return payload["data"]["viewer"]


def summarise(viewer: dict, repositories: list[dict]) -> Stats:
    """Reduce raw API data to panel statistics. Pure, so it can be tested offline."""
    calendar = viewer["contributionsCollection"]["contributionCalendar"]
    # The API's ordering is not a documented guarantee, so sort by date here.
    days = sorted(
        (date.fromisoformat(day["date"]), day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    )

    sizes: Counter[str] = Counter()
    for repository in repositories:
        for edge in repository["languages"]["edges"]:
            if edge["node"]["name"] not in EXCLUDED_LANGUAGES:
                sizes[edge["node"]["name"]] += edge["size"]

    total = sum(sizes.values())
    ranked = sorted(sizes.items(), key=lambda item: (-item[1], item[0]))
    languages = tuple(
        Language(name, size / total) for name, size in ranked if size / total >= MIN_LANGUAGE_SHARE
    )
    return Stats(
        total_contributions=calendar["totalContributions"],
        days=tuple(days),
        repositories=viewer["repositories"]["totalCount"],
        languages=languages,
    )


def fetch(token: str) -> Stats:
    """Fetch everything for the token's owner, following repository pagination."""
    repositories: list[dict] = []
    cursor = None
    while True:
        viewer = _request(token, cursor)
        page = viewer["repositories"]
        repositories.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return summarise(viewer, repositories)
        cursor = page["pageInfo"]["endCursor"]
