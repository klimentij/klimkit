#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE_DIR = ROOT / "inbox" / "to-be-ingested" / "Archive"
DEFAULT_OUTPUT_DIR = DEFAULT_ARCHIVE_DIR / "eda"

TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "best",
    "build",
    "by",
    "can",
    "chatgpt",
    "create",
    "for",
    "from",
    "get",
    "gpt",
    "help",
    "how",
    "i",
    "in",
    "is",
    "it",
    "llm",
    "make",
    "of",
    "on",
    "or",
    "overview",
    "the",
    "this",
    "to",
    "using",
    "with",
    "write",
}

TECHNICAL_KEYWORDS = {
    "agent",
    "api",
    "automation",
    "browser",
    "code",
    "docker",
    "embedding",
    "github",
    "json",
    "knowledge",
    "llm",
    "model",
    "multiagent",
    "playwright",
    "python",
    "rag",
    "react",
    "regex",
    "scrape",
    "selenium",
    "sql",
    "typescript",
    "workflow",
}

CLUSTERS = {
    "ai-systems-and-agents": {
        "agent",
        "agents",
        "ai",
        "chatgpt",
        "embedding",
        "evaluation",
        "finetuning",
        "gpt",
        "knowledge",
        "llm",
        "memory",
        "multiagent",
        "prompt",
        "prompts",
        "rag",
        "reasoning",
        "retrieval",
        "vector",
    },
    "software-engineering": {
        "api",
        "bash",
        "bug",
        "code",
        "css",
        "database",
        "docker",
        "fastapi",
        "git",
        "github",
        "html",
        "javascript",
        "json",
        "kubernetes",
        "playwright",
        "python",
        "react",
        "regex",
        "scrape",
        "scraping",
        "selenium",
        "sql",
        "typescript",
        "xml",
    },
    "research-and-reading": {
        "analysis",
        "arxiv",
        "benchmark",
        "compare",
        "comparison",
        "explain",
        "hypothesis",
        "paper",
        "papers",
        "read",
        "research",
        "review",
        "scientific",
        "science",
        "study",
        "summary",
    },
    "knowledge-systems-and-workflows": {
        "knowledge",
        "note",
        "notes",
        "obsidian",
        "organize",
        "pkm",
        "process",
        "second",
        "system",
        "systems",
        "template",
        "vault",
        "wiki",
        "workflow",
        "workflows",
    },
    "business-product-and-ops": {
        "company",
        "contract",
        "customer",
        "deck",
        "fundraising",
        "invoice",
        "market",
        "meeting",
        "pitch",
        "pricing",
        "product",
        "proposal",
        "roadmap",
        "sales",
        "startup",
        "strategy",
    },
    "finance-legal-and-admin": {
        "accounting",
        "bank",
        "contract",
        "equity",
        "invoice",
        "law",
        "legal",
        "price",
        "pricing",
        "salary",
        "stock",
        "tax",
        "vat",
    },
    "language-learning-and-translation": {
        "conjugation",
        "english",
        "espanol",
        "español",
        "french",
        "german",
        "grammar",
        "italian",
        "japanese",
        "phrase",
        "portuguese",
        "portugues",
        "português",
        "pronunciation",
        "russian",
        "sentence",
        "spanish",
        "translate",
        "translation",
        "ukrainian",
        "verb",
        "vocabulary",
        "vocab",
        "日本語",
    },
    "writing-and-communication": {
        "article",
        "blog",
        "copy",
        "email",
        "essay",
        "headline",
        "linkedin",
        "message",
        "post",
        "rewrite",
        "script",
        "tweet",
        "writing",
    },
    "design-and-ui": {
        "brand",
        "branding",
        "color",
        "design",
        "figma",
        "font",
        "icon",
        "interface",
        "landing",
        "logo",
        "style",
        "typography",
        "ui",
        "ux",
    },
    "personal-life-and-household": {
        "apartment",
        "child",
        "family",
        "gift",
        "home",
        "house",
        "kitchen",
        "recipe",
        "safe",
        "school",
        "travel",
        "vacation",
        "visa",
        "wife",
    },
}

LANGUAGE_LEARNING_HINTS = {
    "translate",
    "translation",
    "grammar",
    "conjugation",
    "vocabulary",
    "vocab",
    "pronunciation",
    "spanish",
    "portuguese",
    "portugues",
    "português",
    "japanese",
    "日本語",
    "espanol",
    "español",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run EDA over an unpacked ChatGPT export.")
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=DEFAULT_ARCHIVE_DIR,
        help="Directory containing conversations-*.json files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write CSV and JSON outputs.",
    )
    parser.add_argument(
        "--sample-count",
        type=int,
        default=12,
        help="Number of sample titles to retain per cluster and owner guess.",
    )
    return parser.parse_args()


def normalize_text(value: str) -> str:
    lowered = value.lower()
    folded = unicodedata.normalize("NFKD", lowered)
    asciiish = "".join(ch for ch in folded if not unicodedata.combining(ch))
    asciiish = asciiish.replace("co-founder", "cofounder").replace("multi-agent", "multiagent")
    return asciiish


def tokenize(value: str) -> list[str]:
    normalized = normalize_text(value)
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{1,}", normalized)


def flatten_text(value: Any) -> list[str]:
    items: list[str] = []
    if isinstance(value, str):
        items.append(value)
    elif isinstance(value, list):
        for part in value:
            items.extend(flatten_text(part))
    elif isinstance(value, dict):
        for key in ("text", "title", "result"):
            if key in value and isinstance(value[key], str):
                items.append(value[key])
        for key in ("parts", "items"):
            if key in value:
                items.extend(flatten_text(value[key]))
    return items


def isoformat_timestamp(timestamp: float | None) -> str:
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def read_conversation_files(archive_dir: Path) -> list[Path]:
    files = sorted(archive_dir.glob("conversations-*.json"))
    if not files:
        raise FileNotFoundError(f"No conversations-*.json files found in {archive_dir}")
    return files


def classify_clusters(text: str) -> list[str]:
    tokens = set(tokenize(text))
    scored: list[tuple[int, str]] = []
    for name, keywords in CLUSTERS.items():
        score = len(tokens & {normalize_text(word) for word in keywords})
        if score:
            scored.append((score, name))
    scored.sort(reverse=True)
    return [name for _, name in scored[:3]]


def classify_owner(text: str, primary_clusters: list[str]) -> tuple[str, str]:
    normalized = normalize_text(text)
    tokens = set(tokenize(normalized))
    wife_score = len(tokens & {normalize_text(word) for word in LANGUAGE_LEARNING_HINTS})
    klim_score = len(tokens & TECHNICAL_KEYWORDS)
    if {"ai-systems-and-agents", "software-engineering", "knowledge-systems-and-workflows"} & set(primary_clusters):
        klim_score += 2

    if wife_score >= 2 and klim_score == 0:
        return "likely-wife", "language-learning signals without technical overlap"
    if wife_score >= 1 and "language-learning-and-translation" in primary_clusters and klim_score == 0:
        return "likely-wife", "explicit human-language signal plus translation cluster"
    if klim_score >= 2 and wife_score == 0:
        return "likely-klim", "technical or systems-heavy signals"
    if wife_score >= 2 and klim_score >= 2:
        return "mixed", "both language-learning and technical signals"
    return "unclear", "insufficient ownership signals"


def message_regions(messages: list[dict[str, Any]]) -> set[str]:
    regions: set[str] = set()
    for message in messages:
        metadata = message.get("metadata", {})
        request_id = metadata.get("request_id")
        if isinstance(request_id, str) and "-" in request_id:
            regions.add(request_id.rsplit("-", 1)[-1])
    return regions


def extract_messages(conversation: dict[str, Any]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for node in conversation.get("mapping", {}).values():
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        if isinstance(message, dict):
            messages.append(message)
    return messages


def message_text(message: dict[str, Any]) -> str:
    content = message.get("content", {})
    return "\n".join(part for part in flatten_text(content) if part).strip()


def first_user_message(messages: list[dict[str, Any]]) -> tuple[str, str]:
    candidates: list[tuple[float, str]] = []
    for message in messages:
        author = message.get("author", {})
        if not isinstance(author, dict) or author.get("role") != "user":
            continue
        text = message_text(message)
        if not text:
            continue
        create_time = message.get("create_time")
        sort_time = float(create_time) if isinstance(create_time, (int, float)) else float("inf")
        candidates.append((sort_time, text))
    if not candidates:
        return "", ""
    candidates.sort(key=lambda item: item[0])
    text = candidates[0][1].strip()
    return text, text.replace("\n", " ")[:300]


def main() -> None:
    args = parse_args()
    files = read_conversation_files(args.archive_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    years = Counter()
    months = Counter()
    models = Counter()
    content_types = Counter()
    message_sources = Counter()
    regions = Counter()
    owner_guesses = Counter()
    cluster_counts = Counter()
    title_tokens = Counter()
    title_bigrams = Counter()
    sample_titles_by_cluster: dict[str, list[str]] = defaultdict(list)
    sample_titles_by_owner: dict[str, list[str]] = defaultdict(list)
    total_messages = 0
    date_min = None
    date_max = None

    for path in files:
        conversations = json.loads(path.read_text(encoding="utf-8"))
        for conversation in conversations:
            title = (conversation.get("title") or "").strip()
            create_time = conversation.get("create_time")
            update_time = conversation.get("update_time")
            messages = extract_messages(conversation)
            total_messages += len(messages)

            first_user_full, first_user_preview = first_user_message(messages)
            combined_text = "\n".join(part for part in [title, first_user_full] if part)
            primary_clusters = classify_clusters(combined_text)
            owner_guess, owner_reason = classify_owner(combined_text, primary_clusters)
            owner_guesses[owner_guess] += 1

            conversation_regions = message_regions(messages)
            for region in conversation_regions:
                regions[region] += 1

            content_type_set = set()
            source_set = set()
            assistant_model_set = set()
            has_dictation = False
            has_browser = False
            has_multimodal = False
            for message in messages:
                metadata = message.get("metadata", {})
                if isinstance(metadata, dict):
                    if metadata.get("dictation") is True:
                        has_dictation = True
                    source = metadata.get("message_source")
                    if isinstance(source, str) and source:
                        source_set.add(source)
                        message_sources[source] += 1
                    model_slug = metadata.get("model_slug") or metadata.get("default_model_slug")
                    if isinstance(model_slug, str) and model_slug:
                        assistant_model_set.add(model_slug)
                content = message.get("content", {})
                if isinstance(content, dict):
                    content_type = content.get("content_type")
                    if isinstance(content_type, str) and content_type:
                        content_type_set.add(content_type)
                        content_types[content_type] += 1
                        if content_type == "multimodal_text":
                            has_multimodal = True
                recipient = message.get("recipient")
                if recipient == "browser":
                    has_browser = True

            if isinstance(create_time, (int, float)):
                created = datetime.fromtimestamp(create_time, tz=UTC)
                year_key = created.strftime("%Y")
                month_key = created.strftime("%Y-%m")
                years[year_key] += 1
                months[month_key] += 1
                date_min = create_time if date_min is None else min(date_min, create_time)
                date_max = create_time if date_max is None else max(date_max, create_time)
            else:
                year_key = ""
                month_key = ""

            default_model = conversation.get("default_model_slug") or ""
            if assistant_model_set:
                default_model = default_model or sorted(assistant_model_set)[0]
            models[default_model or "unknown"] += 1

            row = {
                "source_file": path.name,
                "conversation_id": conversation.get("conversation_id") or conversation.get("id") or "",
                "title": title,
                "create_time_iso": isoformat_timestamp(create_time if isinstance(create_time, (int, float)) else None),
                "update_time_iso": isoformat_timestamp(update_time if isinstance(update_time, (int, float)) else None),
                "year": year_key,
                "year_month": month_key,
                "default_model_slug": default_model or "unknown",
                "message_count": len(messages),
                "first_user_preview": first_user_preview,
                "primary_clusters": "|".join(primary_clusters),
                "owner_guess": owner_guess,
                "owner_reason": owner_reason,
                "request_regions": "|".join(sorted(conversation_regions)),
                "message_sources": "|".join(sorted(source_set)),
                "content_types": "|".join(sorted(content_type_set)),
                "has_dictation": has_dictation,
                "has_browser": has_browser,
                "has_multimodal": has_multimodal,
            }
            rows.append(row)

            for cluster in primary_clusters or ["uncategorized"]:
                cluster_counts[cluster] += 1
                if len(sample_titles_by_cluster[cluster]) < args.sample_count and title:
                    sample_titles_by_cluster[cluster].append(title)
            if len(sample_titles_by_owner[owner_guess]) < args.sample_count and title:
                sample_titles_by_owner[owner_guess].append(title)

            tokens = [token for token in tokenize(title) if token not in TITLE_STOPWORDS]
            title_tokens.update(tokens)
            title_bigrams.update(zip(tokens, tokens[1:]))

    rows.sort(key=lambda row: (row["create_time_iso"], row["conversation_id"]))

    conversations_csv = args.output_dir / "conversation_index.csv"
    with conversations_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "archive_dir": str(args.archive_dir),
        "output_dir": str(args.output_dir),
        "conversation_count": len(rows),
        "message_count": total_messages,
        "date_range": {
            "min": isoformat_timestamp(date_min),
            "max": isoformat_timestamp(date_max),
        },
        "counts": {
            "by_year": dict(years.most_common()),
            "by_month_top_24": dict(months.most_common(24)),
            "by_default_model_slug": dict(models.most_common()),
            "by_primary_cluster": dict(cluster_counts.most_common()),
            "by_owner_guess": dict(owner_guesses.most_common()),
            "by_content_type": dict(content_types.most_common()),
            "by_message_source": dict(message_sources.most_common()),
            "by_request_region": dict(regions.most_common(30)),
        },
        "top_title_tokens": title_tokens.most_common(80),
        "top_title_bigrams": [
            {"bigram": " ".join(pair), "count": count}
            for pair, count in title_bigrams.most_common(50)
        ],
        "sample_titles_by_cluster": dict(sample_titles_by_cluster),
        "sample_titles_by_owner": dict(sample_titles_by_owner),
    }

    summary_json = args.output_dir / "summary.json"
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {conversations_csv}")
    print(f"Wrote {summary_json}")
    print(f"Conversations: {len(rows)}")
    print(f"Messages: {total_messages}")
    print(f"Date range: {summary['date_range']['min']} -> {summary['date_range']['max']}")
    print("Top clusters:")
    for name, count in cluster_counts.most_common(10):
        print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
