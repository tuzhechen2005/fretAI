"use client";

import { useMemo } from "react";
import type { Arrangement, ArrangedChord } from "@/types";
import { TYPE_LABEL } from "./arrangementLabels";
import { ChordDiagram } from "./ChordDiagram";

/**
 * 纯展示卡片：点击选中，底部固定的 ArrangementChatBar 会对选中项生效
 * （自然语言修改的输入/提交逻辑已经搬到那个组件，这里不再各自持有）。
 */
export function ArrangementCard({
  arrangement,
  isSelected,
  onSelect,
}: {
  arrangement: Arrangement;
  isSelected: boolean;
  onSelect: () => void;
}) {
  // 同一个编配里同一种和弦（比如 C5）常会反复出现，指法图按 display 去重展示——
  // 一首歌可能有几十上百个和弦事件，但通常只对应几种到十几种不同和弦形状，
  // 只展示"这个版本会用到哪些指法"，不逐个按时间顺序重复罗列。
  const uniqueChords = useMemo(() => {
    const seen = new Map<string, ArrangedChord>();
    for (const c of arrangement.chords) {
      if (c.fingering && !seen.has(c.display)) seen.set(c.display, c);
    }
    return [...seen.values()];
  }, [arrangement.chords]);

  return (
    <button
      type="button"
      onClick={onSelect}
      className={`flex w-full flex-col gap-5 rounded-xl border p-6 text-left transition-colors ${
        isSelected ? "border-gray-900" : "border-gray-100 hover:border-gray-200"
      }`}
    >
      <div className="flex items-baseline justify-between">
        <h3 className="text-base font-semibold text-gray-900">{TYPE_LABEL[arrangement.type]}</h3>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          {arrangement.capo != null && <span>Capo {arrangement.capo}</span>}
          <span>难度 {arrangement.difficulty}/10</span>
        </div>
      </div>

      {uniqueChords.length > 0 && (
        <div className="flex flex-wrap gap-4 rounded-lg bg-gray-50 p-4 text-gray-700">
          {uniqueChords.map((c) => (
            <div key={c.display} className="flex flex-col items-center">
              <ChordDiagram fingering={c.fingering} position={c.position} />
              <span className="text-xs font-medium text-gray-500">{c.display}</span>
            </div>
          ))}
        </div>
      )}

      {arrangement.notes && <p className="text-sm text-gray-500">{arrangement.notes}</p>}
    </button>
  );
}
