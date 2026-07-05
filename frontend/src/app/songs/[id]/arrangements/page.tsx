/**
 * 编配页（产品文档 §15.3、§15.4）：
 * 多版本卡片对比（难度/capo/横按/推荐原因）+ 和弦图 +
 * 自然语言修改输入框 + 导出按钮。
 */
export default async function ArrangementsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <main className="p-6">
      {/* TODO: <ArrangementCard /> 列表 + <ChordDiagram /> + 修改对话框 + 导出 */}
      <p className="text-gray-500">编配页：song {id}</p>
    </main>
  );
}
