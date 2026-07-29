"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export interface ChordFingering {
  fingering: string;
  position: number;
}

/**
 * 批量查询一组和弦名对应的指法，供 TAB 谱展示用。
 * 分析页只有裸和弦名（没有编配阶段才有的 fingering 数据），所以现查：
 * 先查 voicings 库（静态字典，只覆盖 9 个常见开放和弦），取第一个结果
 * （通常是 open voicing）；查不到就统一回退成 power chord（to_power_chord
 * 支持任意根音，保证每个和弦都能拿到一个可显示的指法）。
 *
 * 按去重后的和弦名查询（不是按事件个数），一首歌通常只有几种到十几种
 * 不同和弦，重复查同一个和弦名没有意义。
 */
export function useChordFingerings(chordNames: string[]): Map<string, ChordFingering> {
  const [fingerings, setFingerings] = useState<Map<string, ChordFingering>>(new Map());
  const uniqueNames = [...new Set(chordNames)];
  const key = uniqueNames.join(",");

  useEffect(() => {
    if (uniqueNames.length === 0) return;
    let cancelled = false;

    async function loadAll() {
      const entries = await Promise.all(
        uniqueNames.map(async (name): Promise<[string, ChordFingering] | null> => {
          try {
            const { voicings } = await api.getVoicings(name);
            if (voicings.length > 0) {
              return [name, { fingering: voicings[0].fingering, position: voicings[0].position }];
            }
            const power = await api.getPowerChordPreview(name);
            return [name, { fingering: power.fingering, position: power.position }];
          } catch (err) {
            console.error(`查询和弦指法失败: ${name}`, err);
            return null; // 单个和弦查询失败不影响其他和弦展示
          }
        }),
      );

      if (cancelled) return;
      setFingerings(new Map(entries.filter((e): e is [string, ChordFingering] => e !== null)));
    }

    loadAll();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return fingerings;
}
