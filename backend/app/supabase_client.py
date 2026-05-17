"""Sixsense Supabase 클라이언트 — PostgREST REST API 래퍼.

루트 .env에서 다음 환경변수 로드:
- SUPABASE_URL              (필수)
- SUPABASE_PUBLISHABLE_KEY  (클라이언트 접근, 신 키 형식 sb_publishable_*)
- SUPABASE_ANON_KEY         (legacy JWT, fallback)
- SUPABASE_SECRET_KEY       (옵션, DDL/admin 작업용 sb_secret_*)

사용:
    from app.supabase_client import sb

    sb.ping()                          # 연결 확인
    sb.select('signals')               # 전체 조회
    sb.insert('signal_data', rows)     # 삽입
    sb.upsert('signal_data', rows, on_conflict='signal_id,week')
"""
import json
import os
from pathlib import Path
from typing import Any, Optional

import requests


def _load_dotenv(env_path: Path):
    """auto_collectors.py와 동일 패턴."""
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        if k and not os.environ.get(k):
            os.environ[k] = v


_PROJECT_ROOT = Path(__file__).parent.parent.parent  # Sixsense/
_load_dotenv(_PROJECT_ROOT / ".env")


class SupabaseClient:
    """경량 Supabase REST 래퍼 (외부 의존 없음)."""

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "").rstrip("/")
        # Priority: SECRET > PUBLISHABLE > ANON (legacy JWT)
        self.secret_key = os.getenv("SUPABASE_SECRET_KEY", "")
        self.pub_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        if not self.url:
            raise RuntimeError("SUPABASE_URL 미설정 (Sixsense/.env 확인)")

    def _key(self, admin: bool = False) -> str:
        """admin=True 면 SECRET 강제, 아니면 PUBLISHABLE → ANON 순"""
        if admin:
            if not self.secret_key:
                raise RuntimeError(
                    "관리자 작업에 SUPABASE_SECRET_KEY 필요. "
                    "Supabase Studio → Project Settings → API → 'service_role' 또는 'secret' 키 복사 후 .env에 추가"
                )
            return self.secret_key
        return self.pub_key or self.anon_key or self.secret_key

    def _headers(self, admin: bool = False, prefer: Optional[str] = None) -> dict:
        key = self._key(admin)
        h = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        if prefer:
            h["Prefer"] = prefer
        return h

    # ── Operations ────────────────────────────────────────────────────────────
    def ping(self) -> dict:
        """연결 확인. 키 종류별 권한 자동 진단."""
        results = {"url": self.url, "keys_present": {
            "publishable": bool(self.pub_key),
            "anon": bool(self.anon_key),
            "secret": bool(self.secret_key),
        }}
        # Try simple query (will fail with 404 if no tables, 401 if auth issue)
        try:
            r = requests.get(
                f"{self.url}/rest/v1/_test_does_not_exist_?select=*&limit=1",
                headers=self._headers(),
                timeout=10,
            )
            results["status"] = r.status_code
            results["auth_ok"] = r.status_code in (200, 404, 406)
            results["body"] = r.text[:200]
        except Exception as e:
            results["error"] = str(e)
        return results

    def select(self, table: str, query: str = "*", filters: Optional[dict] = None, limit: Optional[int] = None) -> list:
        params = {"select": query}
        if filters:
            for k, v in filters.items():
                params[k] = f"eq.{v}"
        if limit:
            params["limit"] = limit
        r = requests.get(f"{self.url}/rest/v1/{table}", headers=self._headers(), params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def insert(self, table: str, rows: list[dict], admin: bool = False) -> Any:
        r = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(admin=admin, prefer="return=minimal"),
            json=rows,
            timeout=60,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"Insert 실패 HTTP {r.status_code}: {r.text[:300]}")
        return {"inserted": len(rows)}

    def upsert(self, table: str, rows: list[dict], on_conflict: str, admin: bool = False) -> Any:
        r = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(admin=admin, prefer="resolution=merge-duplicates,return=minimal"),
            json=rows,
            params={"on_conflict": on_conflict},
            timeout=60,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"Upsert 실패 HTTP {r.status_code}: {r.text[:300]}")
        return {"upserted": len(rows)}

    def delete(self, table: str, filters: dict, admin: bool = True) -> Any:
        params = {k: f"eq.{v}" for k, v in filters.items()}
        r = requests.delete(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(admin=admin),
            params=params,
            timeout=30,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"Delete 실패 HTTP {r.status_code}: {r.text[:300]}")
        return {"deleted_filters": filters}


# Singleton
sb = SupabaseClient()


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(sb.ping(), indent=2))
