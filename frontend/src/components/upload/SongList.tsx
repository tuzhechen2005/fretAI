"use client";

import Link from "next/link";
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
  pending: "text-gray-500",
  analyzing: "text-blue-500",
  done: "text-green-600",
  failed: "text-red-500",
};

export function SongList() {
  const [songs, setSongs] = useState<Song[] | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    api
      .listSongs()
      .then(setSongs)
      .catch((err) => setErrorMessage(err instanceof Error ? err.message : "加载失败"));
  }, []);

  if (errorMessage) return null; // 列表加载失败不影响上传功能，静默忽略
  if (!songs || songs.length === 0) return null;

  return (
    <div className="w-full max-w-sm text-left">
      <h2 className="mb-2 text-sm font-medium text-gray-500">历史记录</h2>
      <ul className="flex flex-col gap-1">
        {songs.map((song) => (
          <li key={song.id}>
            <Link
              href={`/songs/${song.id}`}
              className="flex items-center justify-between rounded-md px-3 py-2 text-sm hover:bg-gray-50"
            >
              <span className="truncate">{song.filename}</span>
              <span className={`shrink-0 pl-2 ${STATUS_COLOR[song.status]}`}>
                {STATUS_LABEL[song.status]}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
