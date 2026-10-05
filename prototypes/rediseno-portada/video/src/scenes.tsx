// PROTOTIPO — escenas del video comparativo.
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import manifestJson from "../public/shots/manifest.json";
import { BrowserFrame, Cursor, INK, MUTED, PhoneFrame, STAGE } from "./components/Frames";
import { fontFamily } from "./fonts";
import { VARIANTS, type VariantMeta } from "./timeline";

type Shot = {
  name: string;
  desktopHeight: number;
  mobileHeight: number;
  sigFrames: number;
  sigLeadFrames: number;
  sigScroll: number;
  click: { x: number; y: number };
};
const manifest = manifestJson as Record<string, Shot>;

const ease = Easing.bezier(0.16, 1, 0.3, 1);
const inOut = Easing.bezier(0.45, 0, 0.25, 1);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const DESK_W = 1136;
const DESK_SCALE = DESK_W / 1440;
const DESK_VH = 900 * DESK_SCALE;
const PHONE_W = 336;
// Escritorio + separación + teléfono, centrados en 1920.
const LEFT = (1920 - (DESK_W + 60 + PHONE_W + 22)) / 2;
const PHONE_SCALE = PHONE_W / 390;
const PHONE_H = 844 * PHONE_SCALE;

const pad = (i: number) => String(i).padStart(3, "0");

const Label: React.FC<{ v: VariantMeta }> = ({ v }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [4, 22], [0, 1], { ...clamp, easing: ease });
  return (
    <div
      style={{
        position: "absolute",
        left: LEFT,
        top: 30,
        display: "flex",
        alignItems: "baseline",
        gap: 22,
        opacity: t,
        transform: `translateX(${(1 - t) * -24}px)`,
        fontFamily,
        color: INK,
      }}
    >
      <span style={{ fontSize: 104, fontWeight: 800, lineHeight: 1, letterSpacing: "-0.04em" }}>{v.n}</span>
      <span style={{ fontSize: 50, fontWeight: 700, letterSpacing: "-0.02em" }}>{v.name}</span>
    </div>
  );
};

const Progress: React.FC<{ active: number }> = ({ active }) => (
  <div style={{ position: "absolute", right: LEFT, top: 70, display: "flex", gap: 10 }}>
    {VARIANTS.map((v) => (
      <span
        key={v.n}
        style={{
          width: v.n === active ? 40 : 12,
          height: 12,
          borderRadius: 6,
          background: v.n === active ? INK : "#3a3c43",
        }}
      />
    ))}
  </div>
);

export const Segment: React.FC<{ v: VariantMeta }> = ({ v }) => {
  const frame = useCurrentFrame();
  const shot = manifest[`v${v.n}`];
  const base = `shots/v${v.n}`;

  // Escritorio: primero un recorrido por la página, luego la animación firma.
  // El recorrido termina exactamente donde empieza la toma de la firma, para que el fundido no salte.
  const maxScroll = Math.max(0, shot.desktopHeight - 900);
  const peak = shot.sigScroll >= 300 ? shot.sigScroll : Math.min(maxScroll, 520);
  const scrollY =
    shot.sigScroll >= 300
      ? interpolate(frame, [12, 118], [0, shot.sigScroll], { ...clamp, easing: inOut })
      : interpolate(frame, [12, 66, 118], [0, peak, shot.sigScroll], { ...clamp, easing: inOut });
  const sigOpacity = interpolate(frame, [116, 130], [0, 1], clamp);
  const CLICK = 150;
  const lead = shot.sigLeadFrames;
  const sigIndex = frame < CLICK ? lead - 1 : Math.min(shot.sigFrames - 1, lead + (frame - CLICK));

  const cx = shot.click.x * DESK_SCALE;
  const cy = shot.click.y * DESK_SCALE;
  const travel = interpolate(frame, [122, CLICK - 4], [0, 1], { ...clamp, easing: ease });
  const pressed = interpolate(frame, [CLICK - 4, CLICK, CLICK + 6], [0, 1, 0], clamp);
  const cursorOpacity =
    interpolate(frame, [120, 128], [0, 1], clamp) * interpolate(frame, [205, 220], [1, 0], clamp);
  const startX = Math.min(DESK_W - 80, cx + 320);
  const startY = Math.min(DESK_VH - 60, cy + 260);

  // Móvil: recorrido continuo.
  const maxMobile = Math.max(0, shot.mobileHeight - 844);
  const mobileY = interpolate(frame, [20, 252], [0, maxMobile], { ...clamp, easing: inOut });

  return (
    <AbsoluteFill style={{ background: STAGE }}>
      <Label v={v} />
      <Progress active={v.n} />
      <div style={{ position: "absolute", left: LEFT, top: 150 }}>
        <BrowserFrame width={DESK_W} viewportHeight={DESK_VH}>
          <Img
            src={staticFile(`${base}/desktop-long.png`)}
            style={{
              position: "absolute",
              width: DESK_W,
              height: shot.desktopHeight * DESK_SCALE,
              transform: `translateY(${-scrollY * DESK_SCALE}px)`,
            }}
          />
          {frame >= 110 ? (
            <Img
              src={staticFile(`${base}/sig/${pad(sigIndex)}.jpg`)}
              style={{ position: "absolute", inset: 0, width: DESK_W, height: DESK_VH, opacity: sigOpacity }}
            />
          ) : null}
          {frame >= 118 ? (
            <Cursor
              x={startX + (cx - startX) * travel}
              y={startY + (cy - startY) * travel}
              pressed={pressed}
              opacity={cursorOpacity}
            />
          ) : null}
        </BrowserFrame>
      </div>
      <div style={{ position: "absolute", left: LEFT + DESK_W + 60, top: 150 }}>
        <PhoneFrame screenWidth={PHONE_W} screenHeight={PHONE_H}>
          <Img
            src={staticFile(`${base}/mobile-long.png`)}
            style={{
              position: "absolute",
              width: PHONE_W,
              height: shot.mobileHeight * PHONE_SCALE,
              transform: `translateY(${-mobileY * PHONE_SCALE}px)`,
            }}
          />
        </PhoneFrame>
      </div>
    </AbsoluteFill>
  );
};

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const W = 1040;
  const VH = 900 * (W / 1440);
  const enter = interpolate(frame, [0, 24], [0, 1], { ...clamp, easing: ease });
  const zoom = interpolate(frame, [0, 315], [1, 1.05], clamp);
  return (
    <AbsoluteFill style={{ background: STAGE, fontFamily, color: INK }}>
      <div
        style={{
          position: "absolute",
          left: 140,
          top: 140,
          opacity: enter,
          transform: `translateY(${(1 - enter) * 20}px)`,
        }}
      >
        <div style={{ fontSize: 26, fontWeight: 600, color: MUTED, marginBottom: 16 }}>Así se ve hoy</div>
        <BrowserFrame width={W} viewportHeight={VH}>
          <Img
            src={staticFile("shots/actual-desktop.png")}
            style={{ width: W, height: VH, transform: `scale(${zoom})`, transformOrigin: "50% 0%" }}
          />
        </BrowserFrame>
      </div>
      <div style={{ position: "absolute", left: 1260, top: 196, width: 540 }}>
        <div
          style={{
            fontSize: 76,
            fontWeight: 800,
            lineHeight: 0.98,
            letterSpacing: "-0.035em",
            opacity: interpolate(frame, [8, 30], [0, 1], clamp),
          }}
        >
          Remote Venezuela Hiring
        </div>
        <div style={{ display: "flex", gap: 12, marginTop: 64 }}>
          {VARIANTS.map((v, i) => {
            const t = interpolate(frame, [212 + i * 6, 232 + i * 6], [0, 1], { ...clamp, easing: ease });
            return (
              <div
                key={v.n}
                style={{
                  width: 88,
                  height: 88,
                  borderRadius: 14,
                  background: INK,
                  color: STAGE,
                  display: "grid",
                  placeItems: "center",
                  fontSize: 48,
                  fontWeight: 800,
                  opacity: t,
                  transform: `translateY(${(1 - t) * 26}px)`,
                }}
              >
                {v.n}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const TW = 324;
  const TH = 900 * (TW / 1440);
  return (
    <AbsoluteFill style={{ background: STAGE, fontFamily, color: INK }}>
      <div
        style={{
          position: "absolute",
          top: 330,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          gap: 28,
        }}
      >
        {VARIANTS.map((v, i) => {
          const t = interpolate(frame, [4 + i * 5, 26 + i * 5], [0, 1], { ...clamp, easing: ease });
          const shot = manifest[`v${v.n}`];
          return (
            <div key={v.n} style={{ width: TW, opacity: t, transform: `translateY(${(1 - t) * 30}px)` }}>
              <div
                style={{
                  width: TW,
                  height: TH,
                  borderRadius: 12,
                  overflow: "hidden",
                  position: "relative",
                  boxShadow: "0 18px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.08)",
                }}
              >
                <Img
                  src={staticFile(`shots/v${v.n}/desktop-long.png`)}
                  style={{ position: "absolute", width: TW, height: shot.desktopHeight * (TW / 1440) }}
                />
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 14, marginTop: 22 }}>
                <span style={{ fontSize: 84, fontWeight: 800, lineHeight: 1, letterSpacing: "-0.04em" }}>{v.n}</span>
                <span style={{ fontSize: 28, fontWeight: 700, color: MUTED }}>{v.name}</span>
              </div>
            </div>
          );
        })}
      </div>
      <div
        style={{
          position: "absolute",
          top: 230,
          left: 0,
          right: 0,
          textAlign: "center",
          fontSize: 30,
          fontWeight: 600,
          color: MUTED,
          opacity: interpolate(frame, [10, 30], [0, 1], clamp),
        }}
      >
        contrataenve.com
      </div>
    </AbsoluteFill>
  );
};
