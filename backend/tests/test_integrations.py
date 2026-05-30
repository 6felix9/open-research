"""Integration tests for the prior-art and sponsor-profiling pipeline components.

Run with:  backend/.venv/bin/pytest backend/tests/test_integrations.py -v -s
All tests that require an API key are skipped automatically when the key is absent.
"""
from __future__ import annotations

import os
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has(key: str) -> bool:
    return bool(os.getenv(key))


# ---------------------------------------------------------------------------
# Mock search (no API key required)
# ---------------------------------------------------------------------------

def test_mock_search_devpost():
    from backend.core.mock_search import mock_search_prior_art

    result = mock_search_prior_art("supabase", "devpost")
    print("\n[mock/devpost]\n", result[:500])
    assert isinstance(result, str)
    assert len(result) > 100
    assert "Supabase" in result or "supabase" in result.lower()


def test_mock_search_x():
    from backend.core.mock_search import mock_search_prior_art

    result = mock_search_prior_art("supabase", "x")
    print("\n[mock/x]\n", result[:500])
    assert isinstance(result, str)
    assert len(result) > 100


# ---------------------------------------------------------------------------
# Jina Reader scraper
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _has("JINA_API_KEY"), reason="JINA_API_KEY not set")
def test_jina_scraper_dead_url():
    """Jina should return something even for a 404 — no crash, no empty string."""
    from backend.core.jina_scraper import scrape_url

    result = scrape_url("https://devpost.com/software/supachat")
    print("\n[jina/dead-url]\n", result[:400])
    assert isinstance(result, str)
    assert len(result) > 0, "Expected non-empty response even for 404"


@pytest.mark.skipif(not _has("JINA_API_KEY"), reason="JINA_API_KEY not set")
def test_jina_scraper_project_content():
    """Jina should return full project content, not just nav chrome."""
    from backend.core.jina_scraper import scrape_url

    # EternaVault — confirmed live Devpost project using Supabase Auth + Storage
    result = scrape_url("https://devpost.com/software/eternavault-8r4hgo")
    print("\n[jina/eternavault]\n", result)
    assert isinstance(result, str)
    assert len(result) > 500, "Expected substantial project content"
    # Nav stripping should have worked — actual project sections must be present
    assert "Inspiration" in result or "What it does" in result or "How we built" in result, \
        "Expected project body sections, got nav boilerplate instead"
    assert "Supabase" in result, "Expected sponsor mention in project content"


@pytest.mark.skipif(not _has("JINA_API_KEY"), reason="JINA_API_KEY not set")
def test_jina_scraper_hackmate():
    """Second real project — HackMate — verifies Jina works across different Devpost pages."""
    from backend.core.jina_scraper import scrape_url

    # HackMate — Supabase Auth + Realtime, interesting RLS schema challenges
    result = scrape_url("https://devpost.com/software/hackmatch-rnbufk")
    print("\n[jina/hackmate]\n", result)
    assert isinstance(result, str)
    assert len(result) > 500
    assert "Supabase" in result
    assert any(kw in result for kw in ("Inspiration", "How we built", "Challenges", "What it does")), \
        "Expected project body sections"


# ---------------------------------------------------------------------------
# Exa search (Devpost domain-filtered + broad X/community)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _has("EXA_API_KEY"), reason="EXA_API_KEY not set")
def test_exa_devpost():
    from backend.core.exa_search import exa_search_prior_art

    result = exa_search_prior_art("Supabase", "devpost")
    print("\n[exa/devpost]\n", result[:800])
    assert isinstance(result, str)
    assert "devpost.com" in result.lower() or len(result) > 50, \
        "Expected Devpost URLs or content from Exa"


@pytest.mark.skipif(not _has("EXA_API_KEY"), reason="EXA_API_KEY not set")
def test_exa_x():
    from backend.core.exa_search import exa_search_prior_art

    result = exa_search_prior_art("Supabase", "x")
    print("\n[exa/x]\n", result[:800])
    assert isinstance(result, str)
    assert len(result) > 50, "Expected community signal results from Exa"


# ---------------------------------------------------------------------------
# Integration: Exa discovery → scraper pipeline (end-to-end)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _has("EXA_API_KEY"), reason="EXA_API_KEY not set")
@pytest.mark.skipif(not _has("JINA_API_KEY"), reason="JINA_API_KEY not set")
def test_integration_exa_devpost_jina():
    """Exa discovers Devpost URLs → Jina scrapes them. Verifies scraping actually fired."""
    from backend.core.exa_search import exa_search_prior_art

    result = exa_search_prior_art("Supabase", "devpost")
    print("\n[integration: exa+jina/devpost]\n", result[:1200])
    assert "devpost.com" in result.lower(), "Expected Devpost URLs from Exa"
    assert "Full content:" in result, \
        "Expected 'Full content:' — Jina scraping did not fire on Exa-discovered URLs"
    assert any(kw in result for kw in ("Inspiration", "How we built", "What it does", "Challenges")), \
        "Expected project body sections in Jina-scraped content, not nav boilerplate"


@pytest.mark.skipif(not _has("EXA_API_KEY"), reason="EXA_API_KEY not set")
def test_integration_exa_x_highlights_only():
    """X source uses Exa highlights only — verifies no scraping is attempted."""
    from backend.core.exa_search import exa_search_prior_art

    result = exa_search_prior_art("Supabase", "x")
    print("\n[integration: exa/x highlights]\n", result[:800])
    assert len(result) > 50
    assert "Full content:" not in result, \
        "X should use Exa highlights only — scraping is not wired for this source"


# ---------------------------------------------------------------------------
# GitHub REST API scraper
# ---------------------------------------------------------------------------

def test_github_scraper():
    """No token required — public API. supabase/supabase is a stable, well-known repo."""
    from backend.core.github_scraper import scrape_github_repo

    result = scrape_github_repo("https://github.com/supabase/supabase")
    print("\n[github/supabase-supabase]\n", result)
    assert isinstance(result, str)
    assert len(result) > 100
    assert "Stars:" in result
    assert "supabase" in result.lower()
    assert "README" in result


@pytest.mark.skipif(not _has("EXA_API_KEY"), reason="EXA_API_KEY not set")
def test_exa_github():
    from backend.core.exa_search import exa_search_prior_art

    result = exa_search_prior_art("Supabase", "github")
    print("\n[exa/github]\n", result[:800])
    assert isinstance(result, str)
    assert "github.com" in result.lower()
    assert len(result) > 100


@pytest.mark.skipif(not _has("EXA_API_KEY"), reason="EXA_API_KEY not set")
def test_integration_exa_github_rest_api():
    """Exa discovers GitHub URLs → REST API enriches them. Verifies scraping actually fired."""
    from backend.core.exa_search import exa_search_prior_art

    result = exa_search_prior_art("Supabase", "github")
    print("\n[integration: exa+github-api]\n", result[:1200])
    assert "github.com" in result.lower(), "Expected GitHub URLs from Exa"
    assert "Full content:" in result, \
        "Expected 'Full content:' — GitHub REST API scraping did not fire on Exa-discovered URLs"
    assert "Stars:" in result, \
        "Expected 'Stars:' from GitHub repo metadata"
    assert "README" in result, \
        "Expected README excerpt from GitHub REST API"


# ---------------------------------------------------------------------------
# Firecrawl via fetch_url_contents
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.skipif(not _has("FIRECRAWL_API_KEY"), reason="FIRECRAWL_API_KEY not set")
async def test_firecrawl_fetch():
    from backend.core.fetch_urls import fetch_url_contents

    result = await fetch_url_contents(["https://supabase.com/docs"])
    print("\n[firecrawl/fetch]\n", result[:800])
    assert isinstance(result, str)
    assert len(result) > 200, "Expected substantial markdown from Firecrawl"
    assert "supabase" in result.lower(), "Expected Supabase content"
