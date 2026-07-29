import { SongHeader } from "@/components/analysis/SongHeader";

/**
 * 分析页（page.tsx）和编配页（arrangements/page.tsx）共享这一层：
 * SongHeader（播放器+时间轴）常驻，路由在两者间切换时不会被卸载重建。
 */
export default async function SongLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="mx-auto max-w-3xl px-8 py-10">
      <SongHeader songId={id} />
      <div className="mt-8">{children}</div>
    </div>
  );
}
