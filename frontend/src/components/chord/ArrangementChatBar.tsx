"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { Arrangement } from "@/types";
import { TYPE_LABEL } from "./arrangementLabels";

/**
 * 底部固定输入框（ChatGPT 风格）：对当前选中的编配版本生效。
 * 从原来每张卡片各自的输入框收拢成一个全局输入框，
 * 用 selected.arrangement_id 明确告诉用户正在修改哪个版本。
 */
export function ArrangementChatBar({
  songId,
  selected,
  onUpdated,
}: {
  songId: string;
  selected: Arrangement;
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
      const result = await api.modifyArrangement(songId, selected.arrangement_id, message);
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
    <div className="sticky bottom-0 -mx-8 border-t border-gray-100 bg-white px-8 py-4">
      <p className="text-xs text-gray-400">
        正在修改：<span className="text-gray-600">{TYPE_LABEL[selected.type]}</span>
      </p>
      <div className="mt-2 flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="用自然语言修改，比如“降两调”"
          className="flex-1 rounded-md border border-gray-200 px-3 py-2 text-sm outline-none focus:border-gray-400"
        />
        <button
          onClick={handleSubmit}
          disabled={!message.trim() || status === "submitting"}
          className="shrink-0 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-gray-700 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
        >
          {status === "submitting" ? "处理中…" : "修改"}
        </button>
      </div>
      {reply && (
        <p className={`mt-2 text-sm ${status === "error" ? "text-red-500" : "text-gray-500"}`}>
          {reply}
        </p>
      )}
    </div>
  );
}
