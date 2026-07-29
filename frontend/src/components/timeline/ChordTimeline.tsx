"use client";

import { useEffect, useRef } from "react";
import type { ChordEvent } from "@/types";

/**
 * 和弦时间轴：每个色块宽度正比于该和弦的实际时长（end - start），
 * currentTime 落在哪个 [start, end) 区间就高亮哪块，点击可跳转播放。
 *
 * 用"每秒固定像素宽度"而不是"占容器百分比"：和弦多、单个时长短时，
 * 百分比宽度会把色块压得放不下文字；改成固定像素比例 + 横向滚动，
 * 保证每个色块有最小可读宽度，同时仍然保留"宽度正比于真实时长"的
 * 时间轴语义（不用 flex-wrap 换行——换行后"宽度比例"就没有意义了，
 * 不再是一条连续的时间线）。
 *
 * 当前播放的和弦块会自动横向滚动到容器可视区域中间（类似视频剪辑软件
 * 的播放头体验），不需要用户自己在长长的时间轴里找播放到哪了。
 *
 * "按小节排列"（产品文档 README 原话）需要用 BPM/拍号推算小节边界，
 * 这里先用更直接的"按实际时长比例"实现，小节网格线留待后续再加。
 */
const PIXELS_PER_SECOND = 40;
const MIN_BLOCK_WIDTH = 32;

export function ChordTimeline({
  chords,
  currentTime,
  onSeek,
}: {
  chords: ChordEvent[];
  currentTime: number;
  onSeek: (time: number) => void;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const activeBlockRef = useRef<HTMLButtonElement>(null);
  const activeIndex = chords.findIndex((c) => currentTime >= c.start && currentTime < c.end);

  useEffect(() => {
    const container = scrollRef.current;
    const activeBlock = activeBlockRef.current;
    if (!container || !activeBlock) return;

    // 不用 offsetLeft：它是相对于"最近的已定位祖先"计算的，而这个滚动容器
    // 没有设置 position，会一路往上找到页面级祖先，把侧边栏宽度也算进去，
    // 导致滚动距离算得远超实际内容宽度（被浏览器钳制到滚动条最大值，
    // 反而把目标块滚出视野）。改用 getBoundingClientRect 算视口坐标系下的
    // 相对位置差，不受"谁是已定位祖先"影响。
    const containerRect = container.getBoundingClientRect();
    const blockRect = activeBlock.getBoundingClientRect();
    const blockCenterInContainer =
      blockRect.left - containerRect.left + container.scrollLeft + blockRect.width / 2;
    const targetScrollLeft = blockCenterInContainer - container.clientWidth / 2;
    container.scrollTo({ left: targetScrollLeft, behavior: "smooth" });
  }, [activeIndex]);

  if (chords.length === 0) return null;

  const totalWidth = chords.reduce(
    (sum, c) => sum + Math.max((c.end - c.start) * PIXELS_PER_SECOND, MIN_BLOCK_WIDTH),
    0,
  );

  return (
    <div>
      <div ref={scrollRef} className="w-full overflow-x-auto rounded-lg border border-gray-100">
        <div className="flex h-11">
          {chords.map((c, i) => {
            const isActive = i === activeIndex;
            const width = Math.max((c.end - c.start) * PIXELS_PER_SECOND, MIN_BLOCK_WIDTH);
            return (
              <button
                key={i}
                ref={isActive ? activeBlockRef : undefined}
                onClick={() => onSeek(c.start)}
                title={`${c.chord}（${c.start.toFixed(1)}s - ${c.end.toFixed(1)}s，置信度 ${c.confidence.toFixed(2)}）`}
                style={{ width: `${width}px` }}
                className={`flex shrink-0 items-center justify-center overflow-hidden border-r border-gray-100 text-xs font-medium transition-colors last:border-r-0 ${
                  isActive ? "bg-gray-900 text-white" : "text-gray-600 hover:bg-gray-50"
                }`}
              >
                <span className="truncate px-1">{c.chord}</span>
              </button>
            );
          })}
        </div>
      </div>
      {/* 单行 + 横向滚动的布局在 macOS 触控板默认隐藏滚动条的情况下不容易被发现，
          总宽度超出一屏（粗略估计用 640px）时才提示，避免短和弦进行也显示这行字。 */}
      {totalWidth > 640 && (
        <p className="mt-2 text-xs text-gray-400">← 可左右滑动查看完整和弦进行 →</p>
      )}
    </div>
  );
}
