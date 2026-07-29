"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { Arrangement } from "@/types";

const TYPE_LABEL: Record<Arrangement["type"], string> = {
  acoustic_beginner: "木吉他新手版",
  acoustic_strumming: "木吉他弹唱版",
  electric_power_chord: "电吉他 Power Chord 版",
  electric_original: "原曲感电吉他版",
  high_position_triads: "高把位三和弦版",
};

export function ArrangementCard({
  songId,
  arrangement,
  onUpdated,
}: {
  songId: string;
  arrangement: Arrangement;
  onUpdated: (updated: Arrangement) => void;
}) {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");

  async function handleSubmit() {
    if (!message.trim()) return;
    setStatus("submitting");
    setReply("");
    try {
      const result = await api.modifyArrangement(songId, arrangement.arrangement_id, message);
      onUpdated(result.arrangement);
      setReply(result.reply);
      setMessage("");
      setStatus("idle");
    } catch (err) {
      setStatus("error");
      setReply(err instanceof Error ? err.message : "修改失败，请重试");
    }
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-gray-200 p-5">
      <div className="flex items-baseline justify-between">
        <h3 className="text-lg font-semibold">{TYPE_LABEL[arrangement.type]}</h3>
        <span className="text-sm text-gray-500">难度 {arrangement.difficulty}/10</span>
      </div>

      {arrangement.capo != null && (
        <p className="text-sm text-gray-500">Capo：第 {arrangement.capo} 品</p>
      )}

      <div className="flex flex-wrap gap-2">
        {arrangement.chords.map((c, i) => (
          <span
            key={i}
            className="rounded-md border border-gray-200 px-3 py-1 text-sm"
            title={`指法 ${c.fingering || "—"}，第 ${c.position} 品`}
          >
            {c.display}
          </span>
        ))}
      </div>

      {arrangement.notes && <p className="text-sm text-gray-600">{arrangement.notes}</p>}

      <div className="mt-2 flex gap-2 border-t border-gray-100 pt-4">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="用自然语言修改，比如“降两调”"
          className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm"
        />
        <button
          onClick={handleSubmit}
          disabled={!message.trim() || status === "submitting"}
          className="rounded-md bg-gray-900 px-4 py-1.5 text-sm font-medium text-white disabled:opacity-40"
        >
          {status === "submitting" ? "处理中..." : "修改"}
        </button>
      </div>
      {reply && (
        <p className={`text-sm ${status === "error" ? "text-red-500" : "text-gray-500"}`}>
          {reply}
        </p>
      )}
    </div>
  );
}
