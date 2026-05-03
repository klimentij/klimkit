#!/usr/bin/env python3
"""
Lightweight EDA for a split ChatGPT export archive.

The script reads conversations directly from a zip archive, extracts
conversation-level metadata, writes a flat CSV of titles + first-user prompts,
and produces a compact JSON summary oriented toward pre-ingest topic design.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZipFile


TITLE_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-\+/#\.]*")
WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-\+/#\.]*")
DEVICE_KEY_RE = re.compile(
    r"(device|user[_-]?agent|platform|browser|mobile|ios|iphone|ipad|android|"
    r"client|app[_-]?version|locale|timezone|tz|language)",
    re.IGNORECASE,
)
DEVICE_VALUE_RE = re.compile(
    r"\b(ios|iphone|ipad|android|macos|windows|linux|chrome|safari|firefox|"
    r"mobile|desktop|tablet|locale|timezone|en-us|pt-br|ja-jp|es-es)\b",
    re.IGNORECASE,
)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "best",
    "build",
    "by",
    "can",
    "code",
    "create",
    "for",
    "from",
    "get",
    "how",
    "i",
    "in",
    "into",
    "is",
    "it",
    "make",
    "my",
    "of",
    "on",
    "or",
    "s",
    "should",
    "the",
    "this",
    "to",
    "using",
    "with",
    "write",
    "you",
    "your",
}


CATEGORY_RULES: list[tuple[str, list[str]]] = [
    (
        "language_learning",
        [
            "portuguese",
            "japanese",
            "spanish",
            "grammar",
            "vocabulary",
            "conjugation",
            "verb tense",
            "translate",
            "translation",
            "hiragana",
            "katakana",
            "kanji",
            "jlpt",
            "duolingo",
            "language learning",
            "practice sentence",
            "pronunciation",
            "pronounciation",
        ],
    ),
    (
        "agentic_engineering",
        [
            "agent",
            "agents",
            "agentic",
            "codex",
            "cursor",
            "opencode",
            "claude code",
            "hermes",
            "worktree",
            "mcp",
            "control plane",
            "sandbox",
            "code server",
            "code-server",
            "parallel agent",
            "tooling",
            "ide",
            "long-running",
        ],
    ),
    (
        "knowledge_bases",
        [
            "rag",
            "retrieval",
            "embedding",
            "vector db",
            "vector database",
            "knowledge base",
            "knowledge graph",
            "wiki",
            "second brain",
            "memory system",
            "nerdqa",
            "ingest",
            "chunk",
            "citation",
            "corpus",
        ],
    ),
    (
        "deterministic_automation",
        [
            "pantera",
            "veridian",
            "alpha",
            "manhattan",
            "warehouse",
            "supply chain",
            "workflow automation",
            "voice ai",
            "order management",
            "sop",
            "integration mapping",
            "customer order",
            "automation platform",
            "enterprise ai assistant",
        ],
    ),
    (
        "personal_systems",
        [
            "tailscale",
            "vpn",
            "ssh",
            "tmux",
            "dotfiles",
            "homelab",
            "home server",
            "code-server",
            "coding ops",
            "coding-ops",
            "personal site",
            "personal system",
            "remote setup",
            "tracker",
        ],
    ),
    (
        "computer_vision",
        [
            "ocr",
            "computer vision",
            "scan",
            "crop",
            "image",
            "video",
            "vision model",
            "scancropper",
            "nerdscan",
        ],
    ),
    (
        "decentralized_ai",
        [
            "crypto",
            "web3",
            "blockchain",
            "on-chain",
            "onchain",
            "decentralized",
            "tokenomics",
            "ethereum",
            "solana",
        ],
    ),
    (
        "product_ux_strategy",
        [
            "ux",
            "ui",
            "pricing",
            "landing page",
            "positioning",
            "mvp",
            "go to market",
            "gtm",
            "customer interview",
            "strategy",
            "startup",
            "product",
            "demo",
        ],
    ),
    (
        "coding_debugging",
        [
            "python",
            "javascript",
            "typescript",
            "sql",
            "regex",
            "pandas",
            "react",
            "node",
            "css",
            "html",
            "bug",
            "debug",
            "error",
            "script",
            "function",
            "algorithm",
            "fastapi",
            "docker",
            "bash",
        ],
    ),
]


@dataclass
class ConversationRecord:
    conversation_id: str
    title: str
    create_time: float | None
    update_time: float | None
    year_month: str
    message_count: int
    user_message_count: int
    assistant_message_count: int
    first_user_prompt: str
    first_user_prompt_short: str
    category: str
    category_score: int
    likely_wife: bool
    likely_wife_reason: str
    archived: bool
    do_not_remember: bool
    starred: bool
    memory_scope: str
    default_model_slug: str
    gizmo_type: str
    voice: str
    models_seen: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--zip",
        default="inbox/to-be-ingested/Archive.zip",
        help="Path to the ChatGPT export zip archive.",
    )
    parser.add_argument(
        "--outdir",
        default=".tmp/chatgpt-export-eda",
        help="Directory where CSV and summary JSON will be written.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=12,
        help="Number of example titles to retain per category.",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\x00", " ")).strip()


def truncate(text: str, limit: int = 180) -> str:
    text = normalize_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def dt_bucket(ts: float | None) -> str:
    if not ts:
        return "unknown"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m")


def iter_text_parts(content: dict[str, Any]) -> list[str]:
    if not isinstance(content, dict):
        return []
    parts = content.get("parts")
    if isinstance(parts, list):
        out = []
        for item in parts:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    out.append(text)
        return out
    text = content.get("text")
    if isinstance(text, str):
        return [text]
    return []


def extract_messages(conversation: dict[str, Any]) -> list[dict[str, Any]]:
    messages = []
    mapping = conversation.get("mapping") or {}
    for node in mapping.values():
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        author = message.get("author") or {}
        role = author.get("role")
        content = message.get("content") or {}
        text = "\n".join(iter_text_parts(content)).strip()
        messages.append(
            {
                "role": role,
                "text": text,
                "create_time": message.get("create_time"),
                "metadata": message.get("metadata") or {},
            }
        )
    messages.sort(key=lambda item: (item["create_time"] is None, item["create_time"] or math.inf))
    return messages


def category_score(text: str, keywords: list[str]) -> int:
    score = 0
    for keyword in keywords:
        if keyword in text:
            score += 2 if " " in keyword else 1
    return score


def classify_conversation(title: str, first_prompt: str) -> tuple[str, int]:
    haystack = f"{title}\n{first_prompt}".lower()
    best_category = "uncategorized"
    best_score = 0
    for category, keywords in CATEGORY_RULES:
        score = category_score(haystack, keywords)
        if score > best_score:
            best_category = category
            best_score = score
    return best_category, best_score


def detect_wife_signal(title: str, first_prompt: str) -> tuple[bool, str]:
    haystack = f"{title}\n{first_prompt}".lower()
    reasons = []
    if classify_conversation(title, first_prompt)[0] == "language_learning":
        reasons.append("language_learning")
    for keyword in (
        "translate to portuguese",
        "translate to japanese",
        "translate to spanish",
        "in portuguese",
        "in japanese",
        "in spanish",
        "practice japanese",
        "practice portuguese",
        "practice spanish",
    ):
        if keyword in haystack:
            reasons.append(keyword)
    return bool(reasons), ", ".join(sorted(set(reasons)))


def title_tokens(title: str) -> list[str]:
    tokens = [token.lower() for token in TITLE_TOKEN_RE.findall(title.lower())]
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def bigrams(tokens: list[str]) -> list[str]:
    return [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]


def recursive_scan(
    value: Any,
    all_keys: Counter[str],
    suspicious_keys: Counter[str],
    suspicious_key_examples: dict[str, str],
    suspicious_values: Counter[str],
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_str = str(key)
            all_keys[key_str] += 1
            if DEVICE_KEY_RE.search(key_str):
                suspicious_keys[key_str] += 1
                if key_str not in suspicious_key_examples and isinstance(item, (str, int, float, bool)):
                    suspicious_key_examples[key_str] = truncate(str(item), 140)
            recursive_scan(item, all_keys, suspicious_keys, suspicious_key_examples, suspicious_values)
        return
    if isinstance(value, list):
        for item in value:
            recursive_scan(item, all_keys, suspicious_keys, suspicious_key_examples, suspicious_values)
        return
    if isinstance(value, str):
        candidate = value.strip()
        if len(candidate) <= 120 and DEVICE_VALUE_RE.search(candidate):
            suspicious_values[candidate] += 1


def summarize_examples(records: list[ConversationRecord], limit: int) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_titles: dict[str, set[str]] = defaultdict(set)
    for record in sorted(records, key=lambda item: (item.create_time or math.inf, item.title.lower())):
        bucket = out[record.category]
        if len(bucket) >= limit:
            continue
        if record.title in seen_titles[record.category]:
            continue
        seen_titles[record.category].add(record.title)
        bucket.append(
            {
                "title": record.title,
                "month": record.year_month,
                "prompt": record.first_user_prompt_short,
            }
        )
    return dict(out)


def write_titles_csv(path: Path, records: list[ConversationRecord]) -> None:
    fieldnames = [
        "conversation_id",
        "title",
        "create_time",
        "update_time",
        "year_month",
        "message_count",
        "user_message_count",
        "assistant_message_count",
        "first_user_prompt",
        "category",
        "category_score",
        "likely_wife",
        "likely_wife_reason",
        "archived",
        "do_not_remember",
        "starred",
        "memory_scope",
        "default_model_slug",
        "gizmo_type",
        "voice",
        "models_seen",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "conversation_id": record.conversation_id,
                    "title": record.title,
                    "create_time": record.create_time,
                    "update_time": record.update_time,
                    "year_month": record.year_month,
                    "message_count": record.message_count,
                    "user_message_count": record.user_message_count,
                    "assistant_message_count": record.assistant_message_count,
                    "first_user_prompt": record.first_user_prompt_short,
                    "category": record.category,
                    "category_score": record.category_score,
                    "likely_wife": record.likely_wife,
                    "likely_wife_reason": record.likely_wife_reason,
                    "archived": record.archived,
                    "do_not_remember": record.do_not_remember,
                    "starred": record.starred,
                    "memory_scope": record.memory_scope,
                    "default_model_slug": record.default_model_slug,
                    "gizmo_type": record.gizmo_type,
                    "voice": record.voice,
                    "models_seen": record.models_seen,
                }
            )


def main() -> None:
    args = parse_args()
    zip_path = Path(args.zip)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    records: list[ConversationRecord] = []
    all_keys: Counter[str] = Counter()
    suspicious_keys: Counter[str] = Counter()
    suspicious_key_examples: dict[str, str] = {}
    suspicious_values: Counter[str] = Counter()
    title_token_counts: Counter[str] = Counter()
    title_bigram_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    wife_category_counts: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    top_level_model_counts: Counter[str] = Counter()
    month_counts: Counter[str] = Counter()
    message_counts: list[int] = []
    empty_title_count = 0

    with ZipFile(zip_path) as zf:
        conversation_members = sorted(
            name
            for name in zf.namelist()
            if name.startswith("conversations-") and name.endswith(".json")
        )
        for member in conversation_members:
            with zf.open(member) as handle:
                conversations = json.load(handle)
            for conversation in conversations:
                recursive_scan(
                    conversation,
                    all_keys,
                    suspicious_keys,
                    suspicious_key_examples,
                    suspicious_values,
                )
                messages = extract_messages(conversation)
                message_count = len(messages)
                user_messages = [msg for msg in messages if msg["role"] == "user"]
                assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
                first_user_prompt = next(
                    (msg["text"] for msg in user_messages if msg["text"].strip()),
                    "",
                )
                title = normalize_text(str(conversation.get("title") or "")).strip()
                if not title:
                    empty_title_count += 1
                    title = "(untitled conversation)"
                category, score = classify_conversation(title, first_user_prompt)
                likely_wife, wife_reason = detect_wife_signal(title, first_user_prompt)
                create_time = conversation.get("create_time")
                update_time = conversation.get("update_time")
                ym = dt_bucket(create_time)
                models_seen = sorted(
                    {
                        str(msg["metadata"].get("model_slug"))
                        for msg in assistant_messages
                        if msg["metadata"].get("model_slug")
                    }
                )
                for model in models_seen:
                    model_counts[model] += 1
                top_level_model = str(conversation.get("default_model_slug") or "").strip()
                if top_level_model:
                    top_level_model_counts[top_level_model] += 1
                for token in title_tokens(title):
                    title_token_counts[token] += 1
                for token in bigrams(title_tokens(title)):
                    title_bigram_counts[token] += 1
                category_counts[category] += 1
                if likely_wife:
                    wife_category_counts[category] += 1
                month_counts[ym] += 1
                message_counts.append(message_count)
                records.append(
                    ConversationRecord(
                        conversation_id=str(
                            conversation.get("conversation_id")
                            or conversation.get("id")
                            or ""
                        ),
                        title=title,
                        create_time=create_time,
                        update_time=update_time,
                        year_month=ym,
                        message_count=message_count,
                        user_message_count=len(user_messages),
                        assistant_message_count=len(assistant_messages),
                        first_user_prompt=first_user_prompt,
                        first_user_prompt_short=truncate(first_user_prompt, 220),
                        category=category,
                        category_score=score,
                        likely_wife=likely_wife,
                        likely_wife_reason=wife_reason,
                        archived=bool(conversation.get("is_archived")),
                        do_not_remember=bool(conversation.get("is_do_not_remember")),
                        starred=bool(conversation.get("is_starred")),
                        memory_scope=str(conversation.get("memory_scope") or ""),
                        default_model_slug=top_level_model,
                        gizmo_type=str(conversation.get("gizmo_type") or ""),
                        voice=str(conversation.get("voice") or ""),
                        models_seen=";".join(models_seen),
                    )
                )

    records.sort(key=lambda item: (item.create_time or math.inf, item.title.lower()))

    summary = {
        "zip_path": str(zip_path),
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "conversation_count": len(records),
        "empty_title_count": empty_title_count,
        "month_counts": dict(month_counts.most_common()),
        "category_counts": dict(category_counts.most_common()),
        "wife_likely_count": sum(1 for record in records if record.likely_wife),
        "wife_category_counts": dict(wife_category_counts.most_common()),
        "top_title_tokens": title_token_counts.most_common(80),
        "top_title_bigrams": title_bigram_counts.most_common(80),
        "message_count_summary": {
            "min": min(message_counts) if message_counts else 0,
            "median": statistics.median(message_counts) if message_counts else 0,
            "mean": round(statistics.mean(message_counts), 2) if message_counts else 0,
            "max": max(message_counts) if message_counts else 0,
        },
        "assistant_model_counts": dict(model_counts.most_common(30)),
        "top_level_model_counts": dict(top_level_model_counts.most_common(30)),
        "suspicious_metadata_keys": [
            {
                "key": key,
                "count": count,
                "example_scalar": suspicious_key_examples.get(key, ""),
            }
            for key, count in suspicious_keys.most_common(40)
        ],
        "suspicious_metadata_values": [
            {"value": value, "count": count}
            for value, count in suspicious_values.most_common(40)
        ],
        "category_examples": summarize_examples(records, args.sample_size),
        "wife_examples": [
            {
                "title": record.title,
                "month": record.year_month,
                "reason": record.likely_wife_reason,
                "prompt": record.first_user_prompt_short,
            }
            for record in records
            if record.likely_wife
        ][: args.sample_size * 3],
    }

    titles_csv = outdir / "conversation_titles.csv"
    summary_json = outdir / "summary.json"
    write_titles_csv(titles_csv, records)
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {titles_csv}")
    print(f"Wrote {summary_json}")
    print(f"Conversations: {len(records)}")
    print(f"Likely wife/language-learning conversations: {summary['wife_likely_count']}")
    print("Top categories:")
    for category, count in category_counts.most_common(12):
        print(f"  {category}: {count}")
    print("Suspicious metadata keys:")
    for item in summary["suspicious_metadata_keys"][:12]:
        print(f"  {item['key']}: {item['count']}")


if __name__ == "__main__":
    main()
