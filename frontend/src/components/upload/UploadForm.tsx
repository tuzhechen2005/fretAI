"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";

export function UploadForm() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleUpload() {
    if (!file) return;
    setStatus("uploading");
    setErrorMessage("");
    try {
      const song = await api.uploadSong(file);
      router.push(`/songs/${song.id}`);
    } catch (err) {
      setStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "上传失败，请重试");
    }
  }

  return (
    <div className="flex w-full flex-col items-center gap-4">
      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="w-full max-w-sm text-sm text-gray-500 file:mr-4 file:rounded-md file:border-0 file:bg-gray-900 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-gray-700"
      />
      <button
        onClick={handleUpload}
        disabled={!file || status === "uploading"}
        className="rounded-md bg-gray-900 px-6 py-2 text-sm font-medium text-white disabled:opacity-40"
      >
        {status === "uploading" ? "上传中..." : "上传并分析"}
      </button>
      {status === "error" && <p className="text-sm text-red-500">{errorMessage}</p>}
    </div>
  );
}
