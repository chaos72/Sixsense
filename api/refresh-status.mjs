// Vercel 서버리스 함수 — 최근 refresh 워크플로 실행 상태를 반환.
// 프론트엔드가 12초마다 폴링해서 진행/완료를 표시한다.
const REPO = "chaos72/Sixsense";
const WORKFLOW = "refresh.yml";

export default async function handler(req, res) {
  const token = process.env.GH_DISPATCH_TOKEN;
  try {
    const r = await fetch(
      `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/runs?per_page=1`,
      {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "sixsense-refresh",
        },
      }
    );
    if (!r.ok) {
      res.status(200).json({ status: "unknown", httpError: r.status });
      return;
    }
    const j = await r.json();
    const run = j.workflow_runs && j.workflow_runs[0];
    if (!run) {
      res.status(200).json({ status: "unknown" });
      return;
    }
    res.status(200).json({
      status: run.status, // queued | in_progress | completed
      conclusion: run.conclusion, // success | failure | cancelled | null
      runId: run.id,
      createdAt: run.created_at,
      updatedAt: run.updated_at,
    });
  } catch (e) {
    res.status(500).json({ error: String(e).slice(0, 200) });
  }
}
