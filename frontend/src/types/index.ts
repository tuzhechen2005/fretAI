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
}
