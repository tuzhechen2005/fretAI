/**
 * 分析页（产品文档 §15.2）：
 * 顶部歌曲信息（Key/BPM），中间波形 + 和弦时间轴，
 * 左侧段落结构，底部播放控制（变速/变调/循环）。
 */
export default async function AnalysisPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <main className="p-6">
      {/* TODO: 轮询 GET /songs/{id} 直到分析完成，然后渲染：
          <WaveformView /> + <ChordTimeline /> + <PlayerControls /> */}
      <p className="text-gray-500">分析页：song {id}</p>
    </main>
  );
}
