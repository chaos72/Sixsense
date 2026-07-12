# Changelog

이 저장소는 `v1.0`부터 버전 태그를 시작합니다 (Git 커밋에 `git tag`로 표시).

## [v1.2] — 2026-07-12

iOS 전용앱(PWA) 전환 + 기능 축소. 사용자 요청 4건 반영.

### 추가/변경
- **iOS 전용앱(PWA) 전환**: 앱 매니페스트(`manifest.webmanifest`)·앱 아이콘(180/192/512)·서비스 워커(`sw.js`, 오프라인 지원) 추가. 아이폰 사파리 '홈 화면에 추가' 시 주소창 없는 전체화면 앱으로 실행.
- **iOS 스타일 디자인**: 좁은 화면(≤640px)에서 하단 탭바(대시보드·뉴스·거시·이벤트·정확도) + 세로 1열 카드 레이아웃 + 노치/홈바 안전여백(safe-area) 적용. 데스크톱은 기존 레이아웃 그대로 유지.
- **프록시 신호 14→10개**: 예측 영향도 0%로 실측된 A-2(빅테크 CapEx)·B-2(대만 뉴스 감성)·B-3(Reddit/HN)·B-4(지정학 리스크) 제외. 백테스트 결과 단기 MAPE 제거 전/후 동일(16.53%) → 정확도 영향 없음 확인.
- **글로벌 이벤트에서 '기상이변' 카테고리 제외**: 수집 단계·빌드 단계 양쪽에서 필터.
- **Graph RAG(구리 vs DRAM 선행 영향도) 섹션 제거**: 대시보드 카드 + 상세 모달(S-005) + 관련 참조 전부 정리, 섹션 번호 재정렬(04~08).

---

## [v1.1] — 2026-07-12 (`2e54037`)

기존 기능(UI/화면 구성)은 그대로 유지하고, 데이터·모델·인사이트만 최신화한 버전.

### 변경 사항
- **데이터 21개 신호 전체 재수집**: 정형 7(A-1~A-7) + 비정형 7(B-1~B-7) + 거시 6 + 타겟 1(target-dram), 모두 최신 주차까지 갱신
- **뉴스/이벤트 재수집 + 한글화**: RSS 기반 뉴스 10건 + 이벤트 10건, Groq LLM으로 한글 번역 100% 보장
- **Multi-Model 재학습**:
  - 단기(1~7주): Prophet baseline → **XGBoost(우수 모델, MAPE 11.05%)** / LightGBM(17.86%)
  - 중장기(8~21주): **LSTM(PyTorch, held-out MAPE 9.19%)**
- **차트 연결성 버그 수정 (#19)**: 중장기(LSTM) 예측 시작점을 현재가가 아닌 단기(XGBoost) 예측 끝점에 anchor하여, 차트에서 단기→중장기 구간에 생기던 "-53% 절벽" 현상 제거 (갭 0% 확인)
- **`model_comparison.txt` 파싱 견고화**: 텍스트 포맷 변경에도 깨지지 않도록 종료 마커 의존 정규식 → lookahead 방식으로 교체
- **`build_insight.py` LLM fallback 확장**: Anthropic → Gemini → **Groq(신규)** → 휴리스틱 4단계 안전망

### 배포
- Vercel 자동 재배포 (https://sixsense-eta.vercel.app) — 커밋 push 시 자동 트리거

---

## [v1.0] — 2026-06-11 (`7dcd8f9`)

Phase 7까지의 최초 완성 버전 (KAIST CAIO 10기 6조 발표 기준).

### 주요 기능
- 21개 실데이터 신호 자동 수집 파이프라인 (Yahoo/SEC/FRED/KOSIS/관세청/AWS/Manifold/HN/GPR/RSS)
- Multi-Model 앙상블: Prophet + sklearn GBR/HistGBR(단기) + PyTorch LSTM(중장기)
- LLM 종합 인사이트 (Claude → Gemini → 휴리스틱 3단계 fallback)
- 뉴스/이벤트 100% 한글화 (Groq fallback 최초 적용)
- 14개 화면 UI hand-off (Claude Design 원본 1px 불변) + 12회 사용자 명시 확장
- 동적 날짜/학습 cutoff 처리 + anchor 보정 최초 적용
