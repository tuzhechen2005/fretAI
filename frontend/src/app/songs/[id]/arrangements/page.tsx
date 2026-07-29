/**
 * 编配页（产品文档 §15.3、§15.4）。
 * MVP 简化版：多版本卡片（难度/capo/和弦列表/notes）+ 底部输入框
 * （sticky 贴在视口底部，ChatGPT 风格：选中某张卡片，输入框对选中版本生效）。
 * 播放器/时间轴常驻在共享的 songs/[id]/layout.tsx 里。
 * 导出按钮留待后续迭代。
 */
import { ArrangementsView } from "@/components/chord/ArrangementsView";

export default async function ArrangementsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ArrangementsView songId={id} />;
}
