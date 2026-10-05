import type { Caption } from "@remotion/captions";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { fontFamily } from "../fonts";

// Subtítulos quemados, una línea por frase (no hay voz, así que no hay resaltado por palabra).
export const Subtitles: React.FC<{ captions: Caption[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const current = captions.find((c) => ms >= c.startMs && ms < c.endMs);
  if (!current) return null;

  const fade = 120;
  const opacity = Math.min(
    interpolate(ms, [current.startMs, current.startMs + fade], [0, 1], { extrapolateRight: "clamp" }),
    interpolate(ms, [current.endMs - fade, current.endMs], [1, 0], { extrapolateLeft: "clamp" }),
  );

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 40 }}>
      <div
        style={{
          opacity,
          maxWidth: 1560,
          padding: "12px 26px 14px",
          borderRadius: 12,
          background: "rgba(8, 8, 10, 0.86)",
          color: "#fff",
          fontFamily,
          fontWeight: 600,
          fontSize: 44,
          lineHeight: 1.22,
          textAlign: "center",
          letterSpacing: "-0.005em",
          textWrap: "balance",
        }}
      >
        {current.text}
      </div>
    </AbsoluteFill>
  );
};
