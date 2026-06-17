# web_search.py

from or_client import client
from utils.knowledge_manager import get_answer, store_answer


def _ddg_search(query: str, max_results: int = 6) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            })

    return results


def _format_ddg(query: str, results: list[dict]) -> str:
    if not results:
        return f"No results found for: {query}"

    lines = [f"Search results for: {query}\n"]

    for i, r in enumerate(results, 1):
        if r.get("title"):
            lines.append(f"{i}. {r['title']}")

        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")

        if r.get("url"):
            lines.append(f"   {r['url']}")

        lines.append("")

    return "\n".join(lines).strip()


def _compare(items: list[str], aspect: str) -> str:
    query = (
        f"Compare {', '.join(items)} in terms of {aspect}. "
        "Give specific facts, pros, cons, and conclusions."
    )

    try:
        return client.chat(
            query,
            system="You are an expert comparison assistant."
        )

    except Exception as e:
        print(f"[WebSearch] OpenRouter compare failed: {e}")

    all_results = {}

    for item in items:
        try:
            all_results[item] = _ddg_search(
                f"{item} {aspect}",
                max_results=3
            )
        except Exception:
            all_results[item] = []

    lines = [
        f"Comparison - {aspect.upper()}",
        "-" * 40
    ]

    for item in items:
        lines.append(f"\n{item}")

        for r in all_results.get(item, [])[:2]:
            if r.get("snippet"):
                lines.append(f"  - {r['snippet']}")

    return "\n".join(lines)


def web_search(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:

    params = parameters or {}

    query = params.get("query", "").strip()
    mode = params.get("mode", "search").lower().strip()
    items = params.get("items", [])
    aspect = params.get("aspect", "general").strip() or "general"

    if not query and not items:
        return "Please provide a search query."

    # Cache lookup
    if query:
        cached = get_answer(query)

        if cached:
            print("[Knowledge] Cache hit")
            return cached

    if items and mode != "compare":
        mode = "compare"

    if player:
        player.write_log(
            f"[Search] {query or ', '.join(items)}"
        )

    print(
        f"[WebSearch] Query: {query!r}  Mode: {mode}"
    )

    # Compare Mode
    if mode == "compare" and items:
        try:
            result = _compare(items, aspect)

            if result:
                store_answer(
                    f"compare:{','.join(items)}:{aspect}",
                    result
                )

            return result

        except Exception as e:
            print(f"[WebSearch] Compare failed: {e}")
            return f"Comparison failed: {e}"

    # DuckDuckGo Search
    try:
        results = _ddg_search(query)

        search_result = _format_ddg(query, results)
        q = query.lower()
        if (
            "news" in q
            or "latest" in q
            or "today" in q
            or "update" in q
            or "headline" in q
        ):
            headlines = []

            for r in results[:5]:
                title = r.get("title", "")
                snippet = r.get("snippet", "")

                if title:
                    headlines.append(
                    f"• {title}\n{snippet}"
                )

            return "\n\n".join(headlines)



        answer = search_result

        try:
            answer = client.chat(
                f"""
user Question: {query}

Search Results:
{search_result}

INSTRUCTIONS:
- Answer the question directly.
- Extract facts from the search results.
- NEVER say:
  - "the search results show"
  - "the provided search results"
  - "the links indicate"
  - "visit the website"
  - "according to the search results"
- NEVER describe the search results.
- If the query is news, provide the latest news headlines and details.
- If the answer exists in the search results, state it directly.
- Respond naturally as an AI assistant.

FINAL ANSWER:
"""

            )

        except Exception as ai_error:
            print(
                f"[WebSearch] AI extraction failed: {ai_error}"
            )

        if answer:
            store_answer(query, answer)

        print(
            f"[WebSearch] DDG: {len(results)} result(s)."
        )

        return answer

    except Exception as e:
        print(
            f"[WebSearch] All backends failed: {e}"
        )
        return f"Search failed: {e}"