"""Tavily web research for Mode 2 — job/domain discovery."""

from __future__ import annotations

from datetime import datetime

from tavily import TavilyClient
from src.config import TAVILY_API_KEY


def get_tavily_client() -> TavilyClient:
    """Create a Tavily client."""
    return TavilyClient(api_key=TAVILY_API_KEY)


def research_domain_problems(
    domain: str,
    role_type: str,
    company_type: str,
    max_results: int = 5,
) -> list[dict]:
    """
    Search for recurring problems in a domain/role using Tavily.

    Returns a list of search results with title, url, and content.
    """
    client = get_tavily_client()

    year = datetime.now().year

    queries = [
        f"{domain} {role_type} challenges problems {year}",
        f"{company_type} {domain} {role_type} blog pain points",
        f"{domain} {role_type} job posting common requirements skills gap",
    ]

    all_results = []
    seen_urls = set()

    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
            )
            for result in response.get("results", []):
                url = result.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(
                        {
                            "title": result.get("title", ""),
                            "url": url,
                            "content": result.get("content", ""),
                        }
                    )
        except Exception as e:
            # Log but don't crash — the bot can fall back to asking the user
            print(f"Tavily search failed for '{query}': {e}")

    return all_results


def format_research_for_prompt(results: list[dict]) -> str:
    """
    Format Tavily results into a string the LLM can use to identify
    recurring domain problems.
    """
    if not results:
        return "No research results found. Ask the user what they've seen companies in this space post about."

    lines = [
        "Here is what I found from engineering blogs, job postings, and industry content:\n"
    ]
    for i, r in enumerate(results, 1):
        lines.append(f"Source {i}: {r['title']}")
        lines.append(f"URL: {r['url']}")
        lines.append(f"Content: {r['content'][:500]}")
        lines.append("")

    lines.append(
        "Based on these sources, identify 3 specific, recurring problems "
        "that a student could build a portfolio project around. "
        "Be concrete — name the problem, who has it, and why it's painful."
    )
    return "\n".join(lines)
