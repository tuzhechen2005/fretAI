"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Song, SongStatus } from "@/types";

const STATUS_LABEL: Record<SongStatus, string> = {
  pending: "排队中",
  analyzing: "分析中",
  done: "已完成",
  failed: "失败",
};

const STATUS_COLOR: Record<SongStatus, string> = {
  pending: "text-gray-400",
  analyzing: "text-gray-400",
  done: "text-gray-500",
  failed: "text-red-500",
};

/**
 * 左侧常驻边栏：品牌 + 新建入口 + 历史歌曲列表（ChatGPT 风格的会话列表）。
 * 当前打开的歌曲高亮，方便定位"我在看哪首"。
 */
export function Sidebar() {
  const [songs, setSongs] = useState<Song[]>([]);
  const params = useParams<{ id?: string }>();
  const activeSongId = params?.id;

  useEffect(() => {
    api
      .listSongs()
      .then(setSongs)
      .catch(() => {}); // 侧边栏历史记录加载失败不影响核心上传/查看功能，静默忽略
  }, []);

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-gray-100 bg-gray-50">
      <div className="p-4">
        <Link href="/" className="text-sm font-semibold tracking-tight text-gray-900">
          FretAI
        </Link>
      </div>

      <div className="px-4 pb-2">
        <Link
          href="/"
          className="flex w-full items-center justify-center rounded-md border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100"
        >
          + 上传新歌曲
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-2">
        <h2 className="px-2 pb-2 text-xs font-medium tracking-wide text-gray-400 uppercase">
          历史记录
        </h2>
        <ul className="flex flex-col gap-0.5">
          {songs.map((song) => {
            const isActive = song.id === activeSongId;
            return (
              <li key={song.id}>
                <Link
                  href={`/songs/${song.id}`}
                  className={`flex items-center justify-between rounded-md px-2 py-2 text-sm transition-colors ${
                    isActive ? "bg-gray-200 text-gray-900" : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <span className="truncate">{song.filename}</span>
                  <span className={`shrink-0 pl-2 text-xs ${STATUS_COLOR[song.status]}`}>
                    {STATUS_LABEL[song.status]}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
