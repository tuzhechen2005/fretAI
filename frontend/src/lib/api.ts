/** 后端 API client。所有请求统一走这里，方便加错误处理和鉴权。 */
import type { AgentTrace, Arrangement, Song, SongAnalysisResult } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  uploadSong(file: File): Promise<Song> {
    const form = new FormData();
    form.append("file", file);
    return request("/songs", { method: "POST", body: form });
  },

  getSong: (id: string) => request<Song>(`/songs/${id}`),

  getAnalysis: (id: string) => request<SongAnalysisResult>(`/songs/${id}/analysis`),

  transpose: (id: string, semitones: number) =>
    request<SongAnalysisResult>(`/songs/${id}/transpose?semitones=${semitones}`, {
      method: "POST",
    }),

  generateArrangements: (id: string) =>
    request<{ arrangements: Arrangement[]; trace: AgentTrace }>(`/songs/${id}/arrangements`, {
      method: "POST",
    }),

  listArrangements: (id: string) => request<Arrangement[]>(`/songs/${id}/arrangements`),

  modifyArrangement: (songId: string, arrangementId: string, message: string) =>
    request<{ arrangement: Arrangement; reply: string; trace: AgentTrace }>(
      `/songs/${songId}/arrangements/${arrangementId}/chat?message=${encodeURIComponent(message)}`,
      { method: "POST" },
    ),

  audioUrl: (id: string) => `${BASE}/songs/${id}/audio`,

  exportUrl: (songId: string, arrangementId: string, format: "markdown" | "pdf") =>
    `${BASE}/songs/${songId}/arrangements/${arrangementId}/export?format=${format}`,
};
