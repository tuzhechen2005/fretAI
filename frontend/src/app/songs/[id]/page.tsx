/**
 * 分析页（产品文档 §15.2）。
 * 播放器/Key/BPM/时间轴常驻在共享的 songs/[id]/layout.tsx 里，
 * 这里只渲染"生成吉他编配"入口。
 */
import { AnalysisView } from "@/components/analysis/AnalysisView";

export default async function AnalysisPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <AnalysisView songId={id} />;
}
