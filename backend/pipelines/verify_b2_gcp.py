#!/usr/bin/env python3
"""B-2 GCP BigQuery 준비 상태 진단 + 다음 액션 안내.

실행:
    .venv/bin/python3 pipelines/verify_b2_gcp.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.supabase_client import _load_dotenv  # 동일 로더 재사용
_load_dotenv(Path(__file__).parent.parent.parent / ".env")

print("\n" + "═" * 72)
print("  B-2 GCP BigQuery 준비 상태 진단")
print("═" * 72)

checks = []

# 1. 패키지 설치 확인
try:
    from google.cloud import bigquery
    pkg_ok = True
    checks.append(("✅", "google-cloud-bigquery 설치됨", f"version 사용 가능"))
except ImportError:
    pkg_ok = False
    checks.append(("❌", "google-cloud-bigquery 미설치", ".venv/bin/pip install google-cloud-bigquery"))

# 2. 환경변수 확인
gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
if gac:
    gac_path = Path(gac).expanduser()
    if gac_path.exists():
        size = gac_path.stat().st_size
        checks.append(("✅", "GOOGLE_APPLICATION_CREDENTIALS 설정", f"{gac} ({size}b)"))
        json_ok = True
    else:
        checks.append(("❌", "JSON 파일 미존재", f"path: {gac}"))
        json_ok = False
else:
    checks.append(("⏸", "GOOGLE_APPLICATION_CREDENTIALS 미설정", ".env에 추가 필요"))
    json_ok = False

# 3. JSON 형식 검증
project_id = None
if json_ok:
    import json
    try:
        sa = json.loads(gac_path.read_text())
        project_id = sa.get("project_id")
        sa_email = sa.get("client_email", "?")
        checks.append(("✅", "Service Account JSON 유효", f"project={project_id}, sa={sa_email[:40]}"))
    except Exception as e:
        checks.append(("❌", "JSON 파싱 실패", str(e)[:60]))

# 4. BigQuery 클라이언트 연결
if pkg_ok and json_ok and project_id:
    try:
        from google.cloud import bigquery
        client = bigquery.Client.from_service_account_json(str(gac_path))
        # 간단 쿼리: GDELT public dataset의 첫 행
        q = "SELECT 1 AS test"
        result = list(client.query(q).result(timeout=15))
        if result:
            checks.append(("✅", "BigQuery 쿼리 작동", "SELECT 1 → OK"))
            ready = True
        else:
            checks.append(("⚠️", "쿼리 응답 비어있음", "권한 확인 필요"))
            ready = False
    except Exception as e:
        msg = str(e)[:80]
        checks.append(("❌", "BigQuery 호출 실패", msg))
        ready = False
else:
    ready = False

# 5. GDELT 테이블 접근 (모든 체크 통과 시만)
if ready:
    try:
        gdelt_q = "SELECT COUNT(*) AS n FROM `gdelt-bq.gdeltv2.events_partitioned` WHERE _PARTITIONTIME = TIMESTAMP('2026-01-05') LIMIT 1"
        result = list(client.query(gdelt_q).result(timeout=20))
        n = result[0].n if result else 0
        checks.append(("✅", "GDELT events_partitioned 접근", f"sample row count: {n:,}"))
    except Exception as e:
        checks.append(("⚠️", "GDELT 테이블 접근 실패", str(e)[:80]))

# ── 출력 ──
print()
for sym, label, detail in checks:
    print(f"  {sym} {label:45} | {detail[:60]}")
print()

# ── 다음 액션 ──
print("─" * 72)
if ready:
    print("  🎉 모든 체크 통과! 이제 다음 명령으로 B-2 수집:")
    print("     .venv/bin/python3 pipelines/auto_collectors.py B-2")
else:
    print("  ⏸  다음 단계 (소요 ~15분):")
    if not pkg_ok:
        print("     1. cd backend && .venv/bin/pip install google-cloud-bigquery")
    if not gac:
        print("     2. GCP Console (console.cloud.google.com) 가입 + 결제카드")
        print("     3. 프로젝트 생성 → IAM → Service Accounts → Create")
        print("        Role: BigQuery Data Viewer + BigQuery Job User")
        print("     4. Keys → Add key (JSON) → 다운로드")
        print("     5. 다운로드한 JSON을 안전한 위치로 이동:")
        print("        mkdir -p ~/.config/gcp && mv ~/Downloads/<JSON> ~/.config/gcp/sixsense-bq.json")
        print("     6. .env에 추가:")
        print("        GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcp/sixsense-bq.json")
    elif not json_ok:
        print(f"     2. JSON 파일 경로 확인: {gac}")
    print()
    print("  📖 상세 가이드: docs/09-data-acquisition/key-acquisition-guide.md §2")
print("═" * 72 + "\n")
sys.exit(0 if ready else 1)
