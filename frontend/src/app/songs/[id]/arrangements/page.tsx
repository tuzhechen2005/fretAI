/**
 * 编配页（产品文档 §15.3、§15.4）。
 * MVP 简化版：多版本卡片（难度/capo/和弦列表/notes）+ 自然语言修改输入框。
 * 和弦指法图（ChordDiagram SVG）、导出按钮留待后续迭代。
 */
import { ArrangementsView } from "@/components/chord/ArrangementsView";

export default async function ArrangementsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <main className="mx-auto max-w-3xl p-6">
      <ArrangementsView songId={id} />
    </main>
  );
}
