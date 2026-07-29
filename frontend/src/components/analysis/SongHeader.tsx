"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { AudioPlayer } from "@/components/player/AudioPlayer";
import { ChordTimeline } from "@/components/timeline/ChordTimeline";
import { TabStrip } from "@/components/timeline/TabStrip";
import type { SongAnalysisResult, SongStatus } from "@/types";

const POLL_INTERVAL_MS = 2000;

/**
 * 歌曲信息头部：播放器 + Key/BPM/拍号 + 和弦时间轴。
 * 放进 songs/[id]/layout.tsx，分析页和编配页共享同一份实例——
 * 之前分析页/编配页是两个独立页面各自渲染，点击"生成编配"整页跳转会
 * 把播放器和时间轴卸载掉；提到共享 layout 后跨路由切换不会丢失这块状态。
 */
export function SongHeader({ songId }: { songId: string }) {
  const [status, setStatus] = useState<SongStatus>("pending");
  const [analysis, setAnalysis] = useState<SongAnalysisResult | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  function handleTimeUpdate() {
    if (audioRef.current) setCurrentTime(audioRef.current.currentTime);
  }

  function handleSeek(time: number) {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      audioRef.current.play();
    }
  }

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
    return <p className="text-sm text-red-500">{errorMessage}</p>;
  }

  if (status === "failed") {
    return <p className="text-sm text-red-500">分析失败，请重新上传。</p>;
  }

  if (status !== "done" || !analysis) {
    return (
      <p className="text-sm text-gray-400">
        {status === "analyzing" ? "正在分析音频……" : "排队等待分析……"}
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <AudioPlayer ref={audioRef} songId={songId} onTimeUpdate={handleTimeUpdate} />

      <div className="flex gap-10 rounded-lg bg-gray-50 px-6 py-4">
        <div>
          <span className="text-xs text-gray-400">Key</span>
          <p className="text-base font-semibold text-gray-900">{analysis.key}</p>
        </div>
        <div>
          <span className="text-xs text-gray-400">BPM</span>
          <p className="text-base font-semibold text-gray-900">{Math.round(analysis.bpm)}</p>
        </div>
        <div>
          <span className="text-xs text-gray-400">拍号</span>
          <p className="text-base font-semibold text-gray-900">{analysis.time_signature}</p>
        </div>
      </div>

      <div>
        <h2 className="mb-3 text-xs font-medium tracking-wide text-gray-400 uppercase">
          和弦进行
        </h2>
        <ChordTimeline chords={analysis.chords} currentTime={currentTime} onSeek={handleSeek} />
      </div>

      <div>
        <h2 className="mb-3 text-xs font-medium tracking-wide text-gray-400 uppercase">
          TAB
        </h2>
        <TabStrip chords={analysis.chords} currentTime={currentTime} onSeek={handleSeek} />
      </div>
    </div>
  );
}
