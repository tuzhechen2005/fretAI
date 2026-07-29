/**
 * SVG 和弦品格图。输入指法字符串，按标准吉他和弦图约定渲染：
 * 6 根弦（从左到右 = 6 弦到 1 弦，低音到高音），弦头标 x（不弹）/ o（空弦），
 * 按弦位置画实心圆点，非把位 0 时在图右侧标注起始品格数字。
 *
 * 兼容后端两种指法字符串格式：
 * - 开放和弦格式（voicings.py）：无分隔符，每个字符 = 一根弦，如 "x32010"
 * - power chord 格式（power_chord.py，`f"{fret}-{fret+2}-{fret+2}xxx"`）：
 *   连字符只分隔到倒数第二段，最后一段是"品格数字直接拼上若干个 x"，
 *   没有分隔符，如 "8-10-10xxx"（split("-") 只能切出 3 段，不是 6 根弦）。
 */

const STRING_COUNT = 6;
const FRETS_SHOWN = 5;

/** 每个元素对应一根弦：null = 不弹（x），0 = 空弦，正整数 = 按第几品（相对 baseFret）。 */
function parseFingering(fingering: string): (number | null)[] {
  if (!fingering.includes("-")) {
    // 开放和弦格式：每个字符就是一根弦
    return fingering.split("").map((c) => (c === "x" ? null : parseInt(c, 10)));
  }

  // power chord 格式：前面的段落是纯数字，最后一段可能是"数字+多个x"粘在一起，
  // 用正则把最后一段再拆成"数字 token"和逐个"x token"。
  const segments = fingering.split("-");
  const tokens = segments.slice(0, -1);
  const lastSegmentTokens = segments[segments.length - 1].match(/\d+|x/g) ?? [];
  return [...tokens, ...lastSegmentTokens].map((t) => (t === "x" ? null : parseInt(t, 10)));
}

export function ChordDiagram({ fingering, position }: { fingering: string; position: number }) {
  const frets = parseFingering(fingering);
  if (frets.length !== STRING_COUNT) {
    // 解析失败（比如遇到未预料的格式），不渲染图，避免画出错误指法误导用户
    return null;
  }

  // 图内展示的品格范围：position=0（开放位置）时从空弦画起；
  // position>0 时说明是把位和弦（如 power chord 在 8 品），要在图上方标注品格数字，
  // 图内本身仍从第 1 品格线画起（点的相对位置 = 实际品格 - position + 1）。
  const baseFret = position;

  const width = 120;
  const height = 140;
  const gridTop = 20;
  const gridLeft = 15;
  const gridRight = width - 15;
  const gridBottom = height - 10;
  const stringGap = (gridRight - gridLeft) / (STRING_COUNT - 1);
  const fretGap = (gridBottom - gridTop) / FRETS_SHOWN;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="shrink-0">
      {baseFret > 0 && (
        <text x={gridRight + 4} y={gridTop + fretGap * 0.7} fontSize="10" fill="currentColor">
          {baseFret}fr
        </text>
      )}

      {/* 品丝横线 */}
      {Array.from({ length: FRETS_SHOWN + 1 }, (_, i) => (
        <line
          key={`fret-${i}`}
          x1={gridLeft}
          y1={gridTop + i * fretGap}
          x2={gridRight}
          y2={gridTop + i * fretGap}
          stroke="currentColor"
          strokeWidth={i === 0 && baseFret === 0 ? 3 : 1}
        />
      ))}

      {/* 弦竖线 */}
      {Array.from({ length: STRING_COUNT }, (_, i) => (
        <line
          key={`string-${i}`}
          x1={gridLeft + i * stringGap}
          y1={gridTop}
          x2={gridLeft + i * stringGap}
          y2={gridBottom}
          stroke="currentColor"
          strokeWidth={1}
        />
      ))}

      {/* 每根弦弦头的 x / o 标记，以及按弦位置的实心圆点 */}
      {frets.map((fret, i) => {
        const x = gridLeft + i * stringGap;

        if (fret === null) {
          return (
            <text key={i} x={x} y={gridTop - 6} fontSize="10" textAnchor="middle" fill="currentColor">
              x
            </text>
          );
        }
        if (fret === 0) {
          return (
            <circle
              key={i}
              cx={x}
              cy={gridTop - 8}
              r={3.5}
              fill="none"
              stroke="currentColor"
              strokeWidth={1}
            />
          );
        }

        const relativeFret = fret - baseFret + 1; // 1-based：第一根品丝格是 1
        const y = gridTop + (relativeFret - 0.5) * fretGap;
        return <circle key={i} cx={x} cy={y} r={5} fill="currentColor" />;
      })}
    </svg>
  );
}
