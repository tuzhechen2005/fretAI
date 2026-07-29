/**
 * 分析页（产品文档 §15.2）。
 * MVP 简化版：Key/BPM + 和弦列表，轮询状态直到分析完成。
 * 波形图、时间轴播放高亮、段落结构、播放控制留待后续迭代。
 */
import { AnalysisView } from "@/components/analysis/AnalysisView";

export default async function AnalysisPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <main className="mx-auto max-w-3xl p-6">
      <AnalysisView songId={id} />
    </main>
  );
}
