/** 与后端 Pydantic schema 一一对应（backend/app/schemas/）。 */

export interface Section {
  name: string; // Intro / Verse / Chorus / ...
  start: number;
  end: number;
}

export interface ChordEvent {
  start: number;
  end: number;
  chord: string;
  confidence: number;
  candidates: string[];
  reason?: string;
  user_corrected: boolean;
}

export interface SongAnalysisResult {
  song_id: string;
  key: string;
  bpm: number;
  time_signature: string;
  sections: Section[];
  chords: ChordEvent[];
}

export type ArrangementType =
  | "acoustic_beginner"
  | "acoustic_strumming"
  | "electric_power_chord"
  | "electric_original"
  | "high_position_triads";

export interface ArrangedChord {
  original: string;
  display: string;
  fingering: string; // e.g. "x02210"
  position: number;
  technique: string[];
}

export interface Arrangement {
  arrangement_id: string;
  song_id: string;
  type: ArrangementType;
  difficulty: number; // 1-10
  capo: number | null;
  tuning: string;
  chords: ArrangedChord[];
  notes: string;
}

export type SongStatus = "pending" | "analyzing" | "done" | "failed";

export interface Song {
  id: string;
  filename: string;
  status: SongStatus;
  created_at?: string; // GET /songs 列表接口才带这个字段，upload/getSong 不带
}

/** Agent Tool Use 循环的执行轨迹（backend/app/schemas/trace.py），用于展示 Agent 思考过程。 */
export interface ToolCallRecord {
  tool_name: string;
  arguments: Record<string, unknown>;
  result: unknown;
}

export interface TraceStep {
  role: "tool_call" | "final";
  tool_calls: ToolCallRecord[];
  content: string | null;
}

export interface AgentTrace {
  steps: TraceStep[];
  final_content: string;
}
