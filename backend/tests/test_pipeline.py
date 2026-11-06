"""Offline tests: no network, no API keys."""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from backend.agents.synthesizer import (
    Breakdown,
    IdeaBrief,
    PriorArtRef,
    SynthesisResult,
    _finalize,
)
from backend.core import corpus as corpus_mod
from backend.main import app

SNAPSHOT = {
    "id": "groq",
    "name": "Groq",
    "updated": "2026-01-01",
    "profile": "Fast inference.",
    "prior_art": [
        {"source": "devpost", "title": "Real Project", "url": "https://devpost.com/software/real", "meta": "Devpost", "excerpt": "x"},
    ],
}


def _idea(title: str, url: str, sponsor=10, interest=10, novelty=10, match=99) -> IdeaBrief:
    return IdeaBrief(
        id="x", title=title, pitch="p", stack=["groq"], match=match,
        breakdown=Breakdown(sponsor=sponsor, interest=interest, novelty=novelty),
        difficulty=1, priorArt=PriorArtRef(title="made up", meta="made up", url=url),
        why="w", risks="r", demoMoment="d",
    )


# --- corpus loading ---------------------------------------------------------

def test_load_sponsor_rejects_path_tricks(tmp_path, monkeypatch):
    monkeypatch.setattr(corpus_mod, "CORPUS_DIR", tmp_path)
    (tmp_path / "groq.json").write_text(json.dumps(SNAPSHOT))
    assert corpus_mod.load_sponsor("groq")["name"] == "Groq"
    assert corpus_mod.load_sponsor("../groq") is None
    assert corpus_mod.load_sponsor("nope") is None


# --- synthesizer post-processing -------------------------------------------

def test_finalize_grounds_citations_and_recomputes_scores():
    result = SynthesisResult(synergy="s", ideas=[
        _idea("weak", "https://invented.example", sponsor=5, interest=5, novelty=5, match=95),
        _idea("strong", "https://devpost.com/software/real", sponsor=30, interest=25, novelty=20, match=10),
    ])
    out = _finalize(result, {"groq": SNAPSHOT})

    assert [i.title for i in out.ideas] == ["strong", "weak"]   # re-ranked by computed match
    assert [i.id for i in out.ideas] == ["i1", "i2"]
    assert out.ideas[0].match == 75                              # sum of breakdown, not model's 10
    assert out.ideas[0].priorArt.title == "Real Project"         # citation replaced from corpus
    assert out.ideas[1].priorArt.url == "#"                      # uncited/invented link neutralised


# --- API --------------------------------------------------------------------

def _events(resp) -> list[tuple[str, dict]]:
    events, name = [], None
    for line in resp.iter_lines():
        if line.startswith("event:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("data:") and name:
            events.append((name, json.loads(line.split(":", 1)[1])))
            name = None
    return events


def test_config_reports_server_key(monkeypatch):
    client = TestClient(app)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert client.get("/api/config").json() == {"server_key": False}
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert client.get("/api/config").json() == {"server_key": True}


def test_stream_requires_a_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    r = TestClient(app).post("/api/research/stream", json={"sponsors": ["groq"], "theme": "t"})
    assert r.status_code == 422


def test_stream_validates_input(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = TestClient(app)
    assert client.post("/api/research/stream", json={"sponsors": [], "theme": "t"}).status_code == 422
    assert client.post("/api/research/stream", json={"sponsors": ["groq"], "theme": " "}).status_code == 422


def test_stream_happy_path_uses_header_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    seen = {}

    async def fake_synthesize(**kwargs):
        seen.update(kwargs)
        return SynthesisResult(synergy="s", ideas=[_idea("one", "https://devpost.com/software/real")])

    monkeypatch.setattr("backend.routers.research.synthesize_task", fake_synthesize)
    monkeypatch.setattr("backend.routers.research.load_sponsor", lambda sid: SNAPSHOT if sid == "groq" else None)

    with TestClient(app).stream(
        "POST", "/api/research/stream",
        json={"sponsors": ["Groq", "ghost"], "theme": "t"},
        headers={"X-OpenAI-Key": "sk-user"},
    ) as resp:
        events = _events(resp)

    names = [n for n, _ in events]
    assert names[-1] == "done" and "ideas" in names and "synergy" in names
    assert seen["api_key"] == "sk-user"
    assert list(seen["corpus"]) == ["groq"]
    warnings = [d for n, d in events if n == "log" and d.get("error") and not d.get("final")]
    assert any("ghost" in w["text"] for w in warnings)           # missing sponsor warns, doesn't abort


def test_stream_fails_cleanly_when_no_research(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr("backend.routers.research.load_sponsor", lambda sid: None)
    with TestClient(app).stream("POST", "/api/research/stream", json={"sponsors": ["ghost"], "theme": "t"}) as resp:
        events = _events(resp)
    assert events[-1][0] == "done"
    assert any(d.get("final") and d.get("error") for n, d in events if n == "log")


@pytest.mark.parametrize("bad", ["", "   "])
def test_blank_header_key_falls_back_to_server(monkeypatch, bad):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-server")
    monkeypatch.setattr("backend.routers.research.load_sponsor", lambda sid: None)
    r = TestClient(app).post("/api/research/stream", json={"sponsors": ["x"], "theme": "t"}, headers={"X-OpenAI-Key": bad})
    assert r.status_code == 200
