"""One-off script: compare raw output quality from all three prior-art sources."""
import os, sys, textwrap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
root = os.path.join(os.path.dirname(__file__), "../..")
load_dotenv(os.path.join(root, ".env.local"))
load_dotenv(os.path.join(root, ".env"))

from backend.core.exa_search import exa_search_prior_art

SPONSOR = "Stripe"
DIVIDER = "=" * 80


def show(source_type: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"SOURCE: {source_type.upper()}")
    print(DIVIDER)
    result = exa_search_prior_art(SPONSOR, source_type)
    print(result)
    print(f"\n[Total chars: {len(result)}]")


for src in ("devpost", "github"):
    show(src)
