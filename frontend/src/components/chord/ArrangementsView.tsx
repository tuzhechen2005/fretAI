"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Arrangement } from "@/types";
import { ArrangementCard } from "./ArrangementCard";

export function ArrangementsView({ songId }: { songId: string }) {
  const [arrangements, setArrangements] = useState<Arrangement[] | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const existing = await api.listArrangements(songId);
        if (cancelled) return;

        if (existing.length > 0) {
          setArrangements(existing);
          return;
        }

        // 还没生成过：触发 Guitar Arrangement Agent 生成木吉他版 + 电吉他版
        const { arrangements: generated } = await api.generateArrangements(songId);
        if (cancelled) return;
        setArrangements(generated);
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
    return <p className="text-red-500">{errorMessage}</p>;
  }

  if (arrangements === null) {
    return <p className="text-gray-500">正在生成编配……</p>;
  }

  return (
    <div className="flex flex-col gap-4">
      {arrangements.map((a) => (
        <ArrangementCard
          key={a.arrangement_id}
          songId={songId}
          arrangement={a}
          onUpdated={handleUpdated}
        />
      ))}
    </div>
  );
}
