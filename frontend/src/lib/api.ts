/** 后端 API client。所有请求统一走这里，方便加错误处理和鉴权。 */
import type {
  AgentTrace,
  Arrangement,
  PowerChordPreview,
  Song,
  SongAnalysisResult,
  Voicing,
} from "@/types";

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

  listSongs: () => request<Song[]>("/songs"),

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

  // 注意路径前缀：arrangements.py 的 router 挂载时统一加了 /songs 前缀
  // （router.py: api_router.include_router(arrangements.router, prefix="/songs")），
  // 即使这两个端点定义在 arrangements.py 里跟具体某首歌无关，实际路径也是
  // /songs/chords/... 不是 /chords/...。
  getVoicings: (chordName: string) =>
    request<{ chord: string; voicings: Voicing[] }>(
      `/songs/chords/${encodeURIComponent(chordName)}/voicings`,
    ),

  getPowerChordPreview: (chordName: string) =>
    request<PowerChordPreview>(
      `/songs/chords/${encodeURIComponent(chordName)}/power-chord-preview`,
    ),

  audioUrl: (id: string) => `${BASE}/songs/${id}/audio`,

  exportUrl: (songId: string, arrangementId: string, format: "markdown" | "pdf") =>
    `${BASE}/songs/${songId}/arrangements/${arrangementId}/export?format=${format}`,
};
