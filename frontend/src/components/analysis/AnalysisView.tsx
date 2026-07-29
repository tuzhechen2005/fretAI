"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { SongAnalysisResult, SongStatus } from "@/types";

const POLL_INTERVAL_MS = 2000;

export function AnalysisView({ songId }: { songId: string }) {
  const [status, setStatus] = useState<SongStatus>("pending");
  const [analysis, setAnalysis] = useState<SongAnalysisResult | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const song = await api.getSong(songId);
        if (cancelled) return;
        setStatus(song.status);

        if (song.status === "done") {
          const result = await api.getAnalysis(songId);
          if (cancelled) return;
          setAnalysis(result);
          return; // 拿到结果，停止轮询
        }
        if (song.status === "failed") {
          return; // 分析失败，停止轮询
        }
        // pending / analyzing：继续轮询
        timer = setTimeout(poll, POLL_INTERVAL_MS);
      } catch (err) {
        if (cancelled) return;
        setErrorMessage(err instanceof Error ? err.message : "查询失败");
      }
    }

    poll();

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [songId]);

  if (errorMessage) {
    return <p className="text-red-500">{errorMessage}</p>;
  }

  if (status === "failed") {
    return <p className="text-red-500">分析失败，请重新上传。</p>;
  }

  if (status !== "done" || !analysis) {
    return (
      <p className="text-gray-500">
        {status === "analyzing" ? "正在分析音频……" : "排队等待分析……"}
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex gap-8 text-sm">
        <div>
          <span className="text-gray-500">Key</span>
          <p className="text-lg font-semibold">{analysis.key}</p>
        </div>
        <div>
          <span className="text-gray-500">BPM</span>
          <p className="text-lg font-semibold">{Math.round(analysis.bpm)}</p>
        </div>
        <div>
          <span className="text-gray-500">拍号</span>
          <p className="text-lg font-semibold">{analysis.time_signature}</p>
        </div>
      </div>

      <div>
        <h2 className="mb-2 text-sm font-medium text-gray-500">和弦进行</h2>
        <div className="flex flex-wrap gap-2">
          {analysis.chords.map((c, i) => (
            <span
              key={i}
              className="rounded-md border border-gray-200 px-3 py-1 text-sm"
              title={`${c.start.toFixed(1)}s - ${c.end.toFixed(1)}s，置信度 ${c.confidence.toFixed(2)}`}
            >
              {c.chord}
            </span>
          ))}
        </div>
      </div>

      <Link
        href={`/songs/${songId}/arrangements`}
        className="w-fit rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white"
      >
        生成吉他编配 →
      </Link>
    </div>
  );
}
