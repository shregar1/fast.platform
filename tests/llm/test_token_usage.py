"""Token usage DTO."""

from types import SimpleNamespace

from llm.token_usage import TokenUsage


def test_from_openai_completion() -> None:
    u = SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    resp = SimpleNamespace(usage=u)
    t = TokenUsage.from_openai_completion(resp, model="gpt-4o")
    assert t.prompt_tokens == 10
    assert t.completion_tokens == 20
    assert t.total_tokens == 30
    assert t.model == "gpt-4o"
    assert t.provider == "openai"


def test_from_anthropic_message() -> None:
    u = SimpleNamespace(input_tokens=5, output_tokens=7)
    resp = SimpleNamespace(usage=u)
    t = TokenUsage.from_anthropic_message(resp, model="claude-3")
    assert t.prompt_tokens == 5
    assert t.completion_tokens == 7
    assert t.total_tokens == 12
    assert t.provider == "anthropic"
