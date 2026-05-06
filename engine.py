from openai import OpenAI
import os
import time


GPT_4O_MINI_INPUT_COST_PER_MILLION = 0.15
GPT_4O_MINI_OUTPUT_COST_PER_MILLION = 0.60


def analyze_commentary_score(commentary):
    """
    Sends match commentary to GPT-4 to interpret the current score.
    """
    client = OpenAI(api_key=os.getenv("api_key"))

    system_prompt = """You are a sports data analyst specializing in cricket.
        Analyze the provided commentary and return a JSON object representing the over.
        Include 'over_number', 'over_total_confidence', 'balls' (a list of each delivery),
        and 'total_over_runs'.

        RULES FOR THE 'balls' ARRAY:
        1. For legal deliveries, use 'ball': <number> (1 to 6), 'result': <e.g. '6 runs', '1 run', '0 runs', 'Wicket', 'unknown'>,
        'quality_score' (0.0 to 1.0, where 0.0 = no confidence, 1.0 = certain),
        and optionally 'note' (lowercase) if clarification is needed.
        2. For extras (wide or no ball), include a separate entry with 'extra': 'wide' or 'extra': 'no ball',
        'result': <runs scored on that delivery,which is '1 run'>,
        'quality_score', and optionally 'note'. Do NOT increment the 'ball' counter for extras.
        3. 'result' must always use plural 'runs' even for 1 (e.g. '1 run' is acceptable, '6 runs', '0 runs').
        Use 'Wicket' for dismissals, 'unknown' if the delivery outcome cannot be determined.
        4. 'quality_score' must be 0.0 when result is 'unknown'.
        Use lower scores (e.g. 0.1) when the result is inferred rather than explicitly stated.
        Use 1.0 only when the result is explicitly and unambiguously described.
        5. 'total_over_runs' must be an integer — the sum of all runs scored in the over including extras.
        6. 'total_over_wickets' must be an integer — the sum of all wickets fallen in the over.

        OUTPUT FORMAT EXAMPLE:
        {
        "over_number": 4,
        "over_total_confidence": 0.83,
        "balls": [
            {"ball": 1, "result": "6 runs", "quality_score": 1.0},
            {"ball": 2, "result": "0 runs", "quality_score": 1.0},
            {"extra": "wide", "result": "1 run", "quality_score": 1.0},
            {"ball": 3, "result": "unknown", "quality_score": 0.0, "note": "Technical glitch mentioned"},
            {"ball": 4, "result": "1 run", "quality_score": 1.0},
            {"ball": 5, "result": "0 runs", "quality_score": 0.4, "note": "Inferred from 'defensive stroke'"},
            {"ball": 6, "result": "0 runs", "quality_score": 0.4, "note": "Inferred from 'defensive stroke'"}
        ],
        "total_over_runs": 8,
        "total_over_wickets": 0
        }

        Output ONLY raw JSON. No markdown, no explanation, no backticks."""
    prompt = f"Analyze the following sports commentary and determine the current score: '{commentary}'"

    started_at = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        elapsed_seconds = time.perf_counter() - started_at
        usage = response.usage
        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0

        estimated_cost_usd = (
            (prompt_tokens / 1_000_000) * GPT_4O_MINI_INPUT_COST_PER_MILLION
            + (completion_tokens / 1_000_000) * GPT_4O_MINI_OUTPUT_COST_PER_MILLION
        )

        return {
            "ok": True,
            "analysis": response.choices[0].message.content,
            "elapsed_seconds": elapsed_seconds,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "estimated_cost_inr": estimated_cost_usd * 85.0
        }
    except Exception as e:
        elapsed_seconds = time.perf_counter() - started_at
        return {
            "ok": False,
            "error": str(e),
            "elapsed_seconds": elapsed_seconds,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "estimated_cost_inr": 0.0
        }


if __name__ == "__main__":
    commentary = "The 7th over began with a no ball, the free hit was defended. First ball proper was a dot. A wide was bowled on the second. Second ball was hit for 3. Third ball, a single. Fourth ball, dot. Fifth ball, another wide. Fifth ball proper was smashed for 6. Sixth ball, dot."
    print(analyze_commentary_score(commentary))
