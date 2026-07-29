"use client";

import { forwardRef } from "react";
import { api } from "@/lib/api";

/**
 * 用原生 <audio controls>，浏览器自带播放/暂停/进度条/音量，不用自己造轮子。
 * 后端 GET /songs/{id}/audio 支持 Range 请求，拖动进度条不需要重新下载整个文件。
 * 变速/A-B 循环/波形图留待后续需要时再加（README 规划的 PlayerControls/WaveformView）。
 *
 * 用 forwardRef 暴露底层 <audio> DOM 元素：时间轴高亮需要读 currentTime、
 * 点击和弦块需要设置 currentTime 跳转播放位置，这两个操作都得直接操作
 * audio 元素本身，不能只靠 props 单向传递完成，所以让父组件能拿到 ref。
 */
export const AudioPlayer = forwardRef<HTMLAudioElement, { songId: string; onTimeUpdate?: () => void }>(
  function AudioPlayer({ songId, onTimeUpdate }, ref) {
    return (
      <audio
        ref={ref}
        controls
        preload="metadata"
        src={api.audioUrl(songId)}
        onTimeUpdate={onTimeUpdate}
        className="w-full"
      >
        你的浏览器不支持音频播放。
      </audio>
    );
  },
);
