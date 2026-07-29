import Link from "next/link";

/**
 * 分析页正文：播放器/Key/BPM/时间轴已经提到 songs/[id]/layout.tsx 的
 * SongHeader 里常驻展示，这里只剩"去生成编配"这一个入口。
 */
export function AnalysisView({ songId }: { songId: string }) {
  return (
    <Link
      href={`/songs/${songId}/arrangements`}
      className="w-fit rounded-md bg-gray-900 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-gray-700"
    >
      生成吉他编配 →
    </Link>
  );
}
