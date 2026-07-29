"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Arrangement } from "@/types";
import { ArrangementCard } from "./ArrangementCard";
import { ArrangementChatBar } from "./ArrangementChatBar";

/**
 * 编配区块：渲染在分析页 SongHeader 下方（同一个可滚动页面里，不再单独跳转）。
 * 输入框用 sticky 贴在视口底部，不需要像独立页面那样用高度计算强制拆分
 * "卡片滚动区/固定输入框"。
 */
export function ArrangementsView({ songId }: { songId: string }) {
  const [arrangements, setArrangements] = useState<Arrangement[] | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const existing = await api.listArrangements(songId);
        if (cancelled) return;

        if (existing.length > 0) {
          setArrangements(existing);
          setSelectedId(existing[0].arrangement_id);
          return;
        }

        // 还没生成过：触发 Guitar Arrangement Agent 生成木吉他版 + 电吉他版
        const { arrangements: generated } = await api.generateArrangements(songId);
        if (cancelled) return;
        setArrangements(generated);
        setSelectedId(generated[0]?.arrangement_id ?? null);
      } catch (err) {
        if (cancelled) return;
        setErrorMessage(err instanceof Error ? err.message : "加载编配失败");
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [songId]);

  function handleUpdated(updated: Arrangement) {
    setArrangements((prev) =>
      prev?.map((a) => (a.arrangement_id === updated.arrangement_id ? updated : a)) ?? prev,
    );
  }

  if (errorMessage) {
    return <p className="text-sm text-red-500">{errorMessage}</p>;
  }

  if (arrangements === null) {
    return <p className="text-sm text-gray-400">正在生成编配……</p>;
  }

  const selected = arrangements.find((a) => a.arrangement_id === selectedId) ?? null;

  return (
    <div className="flex flex-col gap-4">
      {arrangements.map((a) => (
        <ArrangementCard
          key={a.arrangement_id}
          arrangement={a}
          isSelected={a.arrangement_id === selectedId}
          onSelect={() => setSelectedId(a.arrangement_id)}
        />
      ))}

      {selected && (
        <ArrangementChatBar songId={songId} selected={selected} onUpdated={handleUpdated} />
      )}
    </div>
  );
}
