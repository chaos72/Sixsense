// Vercel 서버리스 함수 — 아이폰 '수동 갱신' 버튼이 부르는 엔드포인트.
// GitHub Actions 워크플로(refresh.yml)를 workflow_dispatch 로 트리거한다.
// 토큰은 Vercel 환경변수 GH_DISPATCH_TOKEN 에 저장 (코드/클라이언트에 노출 안 됨).
const REPO = "chaos72/Sixsense";
const WORKFLOW = "refresh.yml";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "POST 요청만 허용" });
    return;
  }
  const token = process.env.GH_DISPATCH_TOKEN;
  if (!token) {
    res.status(500).json({ error: "서버에 GH_DISPATCH_TOKEN 이 설정되지 않았습니다 (Vercel 환경변수)" });
    return;
  }
  const gh = (path, init) =>
    fetch(`https://api.github.com/repos/${REPO}/${path}`, {
      ...init,
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "sixsense-refresh",
        ...(init && init.headers),
      },
    });

  try {
    // 이미 실행 중이면 중복 트리거 방지
    const runsRes = await gh(`actions/workflows/${WORKFLOW}/runs?per_page=1`);
    if (runsRes.ok) {
      const runsJson = await runsRes.json();
      const latest = runsJson.workflow_runs && runsJson.workflow_runs[0];
      if (latest && (latest.status === "in_progress" || latest.status === "queued")) {
        res.status(200).json({ status: "already_running", runId: latest.id });
        return;
      }
    }
    // 워크플로 트리거
    const dispatchRes = await gh(`actions/workflows/${WORKFLOW}/dispatches`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ref: "main" }),
    });
    if (dispatchRes.status === 204) {
      res.status(202).json({ status: "triggered", at: Date.now() });
    } else {
      const detail = (await dispatchRes.text()).slice(0, 200);
      res.status(502).json({ error: `GitHub 트리거 실패 (HTTP ${dispatchRes.status})`, detail });
    }
  } catch (e) {
    res.status(500).json({ error: String(e).slice(0, 200) });
  }
}
