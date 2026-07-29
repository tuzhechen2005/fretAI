"use client";

import { useEffect, useRef } from "react";
import { useChordFingerings } from "@/hooks/useChordFingerings";
import type { ChordEvent } from "@/types";

/**
 * 六线谱（TAB）样式的和弦进行展示：6 条横线代表 6 根弦，每个和弦是一列，
 * 在对应弦的线上标品格数字（不弹的弦标 ×）。跟 ChordTimeline 是同一批
 * chords 数据的两种视图，宽度节奏、当前播放高亮/居中滚动逻辑都保持一致，
 * 方便左右对照阅读。
 *
 * 指法数据这里现查（分析页只有裸和弦名，没有编配阶段才有的 fingering）：
 * 见 useChordFingerings —— 优先查 voicings 库，查不到回退成 power chord。
 */
const PIXELS_PER_SECOND = 40;
const MIN_BLOCK_WIDTH = 40;
const STRING_COUNT = 6;
const ROW_HEIGHT = 18;

function parseFingering(fingering: string): (number | null)[] {
  if (!fingering.includes("-")) {
    return fingering.split("").map((c) => (c === "x" ? null : parseInt(c, 10)));
  }
  const segments = fingering.split("-");
  const tokens = segments.slice(0, -1);
  const lastSegmentTokens = segments[segments.length - 1].match(/\d+|x/g) ?? [];
  return [...tokens, ...lastSegmentTokens].map((t) => (t === "x" ? null : parseInt(t, 10)));
}

export function TabStrip({
  chords,
  currentTime,
  onSeek,
}: {
  chords: ChordEvent[];
  currentTime: number;
  onSeek: (time: number) => void;
}) {
  const fingerings = useChordFingerings(chords.map((c) => c.chord));
  const scrollRef = useRef<HTMLDivElement>(null);
  const activeBlockRef = useRef<HTMLButtonElement>(null);
  const activeIndex = chords.findIndex((c) => currentTime >= c.start && currentTime < c.end);

  useEffect(() => {
    const container = scrollRef.current;
    const activeBlock = activeBlockRef.current;
    if (!container || !activeBlock) return;

    const containerRect = container.getBoundingClientRect();
    const blockRect = activeBlock.getBoundingClientRect();
    const blockCenterInContainer =
      blockRect.left - containerRect.left + container.scrollLeft + blockRect.width / 2;
    const targetScrollLeft = blockCenterInContainer - container.clientWidth / 2;
    container.scrollTo({ left: targetScrollLeft, behavior: "smooth" });
  }, [activeIndex]);

  if (chords.length === 0) return null;

  const height = STRING_COUNT * ROW_HEIGHT;

  return (
    <div ref={scrollRef} className="w-full overflow-x-auto rounded-lg border border-gray-100 bg-white">
      <div className="flex" style={{ height }}>
        {chords.map((c, i) => {
          const isActive = i === activeIndex;
          const width = Math.max((c.end - c.start) * PIXELS_PER_SECOND, MIN_BLOCK_WIDTH);
          const fingering = fingerings.get(c.chord);
          const frets = fingering ? parseFingering(fingering.fingering) : null;

          return (
            <button
              key={i}
              ref={isActive ? activeBlockRef : undefined}
              onClick={() => onSeek(c.start)}
              title={`${c.chord}${fingering ? `（第 ${fingering.position} 品）` : ""}`}
              style={{ width, height }}
              className={`relative shrink-0 border-r border-gray-50 transition-colors last:border-r-0 ${
                isActive ? "bg-gray-900" : "hover:bg-gray-50"
              }`}
            >
              {/* 6 条弦线 */}
              {Array.from({ length: STRING_COUNT }, (_, row) => (
                <div
                  key={row}
                  className={isActive ? "absolute right-0 left-0 bg-gray-600" : "absolute right-0 left-0 bg-gray-200"}
                  style={{ top: row * ROW_HEIGHT + ROW_HEIGHT / 2, height: 1 }}
                />
              ))}

              {/* 每根弦上的品格数字 / 不弹标记 */}
              {frets?.map((fret, row) => (
                <span
                  key={row}
                  className={`absolute left-1/2 -translate-x-1/2 text-[10px] font-medium leading-none ${
                    isActive ? "bg-gray-900 text-white" : "bg-white text-gray-700"
                  }`}
                  style={{ top: row * ROW_HEIGHT + ROW_HEIGHT / 2 - 6 }}
                >
                  {fret === null ? "×" : fret}
                </span>
              ))}
            </button>
          );
        })}
      </div>
    </div>
  );
}
