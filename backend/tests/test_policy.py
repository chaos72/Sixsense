"""LLM 공급자 정책 자동 검사 (v2.6.1 재발 방지 장치)

사용자 결정(2026-09): "중국 모델이나 오픈소스 모델 사용 금지. GPT·Gemini·Sonnet 중 하나만, 무료로" → Gemini 무료 티어 단독.
과거에 qwen·gpt-oss(Groq) 사용을 시도했다가 두 번 중단당한 사고가 있었다. 이 시험은 실행되는 코드·설정에
Gemini 외 AI 공급자의 import·호출 주소·키 이름이 들어오면 실패한다. (주석·설명 글은 검사하지 않음)
"""
import ast
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PIPELINES = Path(os.environ.get("SIXSENSE_PIPELINES") or REPO / "backend" / "pipelines")

FORBIDDEN = re.compile(
    r"anthropic|openai|groq|deepseek|qwen|llama|mistral|ollama|openrouter|huggingface|together\.xyz|"
    r"cohere|gpt-oss|ANTHROPIC_API_KEY|OPENAI_API_KEY|GROQ_API_KEY",
    re.IGNORECASE)


def _code_strings_and_imports(path: Path) -> list[str]:
    """파이썬 파일에서 실제로 실행되는 부분만 — import 이름과 문자열 상수(설명 글 제외)."""
    tree = ast.parse(path.read_text())
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant):
                docstrings.add(id(first.value))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            out.append(node.module or "")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            out.append(node.value)
        elif isinstance(node, (ast.Name, ast.Attribute)):
            out.append(node.id if isinstance(node, ast.Name) else node.attr)
    return out


def _non_comment_lines(path: Path, comment: str) -> list[str]:
    return [ln for ln in path.read_text().splitlines() if not ln.strip().startswith(comment)]


def test_파이프라인_코드에_Gemini_외_AI_공급자_없음():
    hits = []
    for p in sorted(PIPELINES.glob("*.py")):
        for s in _code_strings_and_imports(p):
            m = FORBIDDEN.search(s)
            if m:
                hits.append(f"{p.name}: {m.group()} ← {s[:60]!r}")
    assert not hits, "Gemini 외 AI 공급자 흔적:\n" + "\n".join(hits)


def test_주간_작업_설정과_서버_함수에_Gemini_외_AI_키_없음():
    hits = []
    for p in [REPO / ".github/workflows/refresh.yml", *sorted((REPO / "api").glob("*.mjs"))]:
        for ln in _non_comment_lines(p, "#" if p.suffix == ".yml" else "//"):
            m = FORBIDDEN.search(ln)
            if m:
                hits.append(f"{p.name}: {ln.strip()[:80]}")
    assert not hits, "Gemini 외 AI 흔적:\n" + "\n".join(hits)


def test_Gemini_클라이언트는_Gemini_모델과_구글_주소만():
    import gemini_client as gc
    models = set(gc.QUALITY_MODELS) | set(gc.BULK_MODELS)
    assert models and all(m.startswith("gemini-") for m in models), models
    urls = re.findall(r"https?://[^\s\"'{}]+", (PIPELINES / "gemini_client.py").read_text())
    assert urls and all(u.startswith("https://generativelanguage.googleapis.com/") for u in urls), urls
