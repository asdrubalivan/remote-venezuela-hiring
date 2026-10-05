// PROTOTIPO — línea de tiempo del video comparativo y subtítulos.
import type { Caption } from "@remotion/captions";

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

export const INTRO = 315;
export const SEGMENT = 270;
export const OUTRO = 180;
export const TRANSITION = 12;

export type VariantMeta = { n: number; name: string };

export const VARIANTS: VariantMeta[] = [
  { n: 1, name: "Clasificados" },
  { n: 2, name: "Piso de Maiquetía" },
  { n: 3, name: "Boleto" },
  { n: 4, name: "Metro" },
  { n: 5, name: "Guía amarilla" },
];

// Inicio absoluto (en cuadros) de cada escena dentro de la TransitionSeries.
export const SCENE_START = {
  intro: 0,
  segments: VARIANTS.map((_, i) => INTRO - TRANSITION + i * (SEGMENT - TRANSITION)),
  outro: INTRO - TRANSITION + VARIANTS.length * (SEGMENT - TRANSITION),
};

export const TOTAL_FRAMES = SCENE_START.outro + OUTRO;

// Subtítulos (pasados por /humanizer). Tiempos en segundos, relativos a su escena.
type Line = { from: number; to: number; text: string };

const INTRO_LINES: Line[] = [
  { from: 0.4, to: 3.3, text: "Le estoy cambiando el diseño a Remote Venezuela Hiring." },
  { from: 3.4, to: 6.9, text: "La lista de empresas que aceptan, o no, gente desde Venezuela." },
  { from: 7.0, to: 10.1, text: "Hice 5 versiones con el mismo contenido. Tú eliges." },
];

const SEGMENT_LINES: Line[][] = [
  [
    { from: 0.5, to: 4.1, text: "La primera sale de los clasificados del periódico." },
    { from: 4.2, to: 8.6, text: "Las que aceptan quedan encerradas en rojo, como cuando marcábamos avisos." },
  ],
  [
    { from: 0.5, to: 3.6, text: "La segunda es el piso de Maiquetía." },
    { from: 3.7, to: 8.6, text: "Sí, el de la foto de los pies antes de irse. Al filtrar, cambia de color." },
  ],
  [
    { from: 0.5, to: 4.1, text: "La tercera es un boleto de avión: cada empresa es un cupón." },
    { from: 4.2, to: 8.6, text: "Cada una lleva su sello. Si no acepta, le cae el sello rojo." },
  ],
  [
    { from: 0.5, to: 4.1, text: "La cuarta usa los letreros del Metro de Caracas." },
    { from: 4.2, to: 8.6, text: "La lista es una línea y cada empresa, una parada." },
  ],
  [
    { from: 0.5, to: 4.1, text: "La última es la guía de CANTV, la que había en todas las casas." },
    { from: 4.2, to: 8.6, text: "Saltas a la letra y sigues los puntos hasta el estado." },
  ],
];

const OUTRO_LINES: Line[] = [
  { from: 0.4, to: 2.4, text: "¿Con cuál te quedas?" },
  { from: 2.5, to: 5.8, text: "Responde con el número de tu favorita." },
];

const toCaptions = (lines: Line[], sceneStartFrame: number): Caption[] =>
  lines.map((l) => {
    const base = (sceneStartFrame / FPS) * 1000;
    return {
      text: l.text,
      startMs: Math.round(base + l.from * 1000),
      endMs: Math.round(base + l.to * 1000),
      timestampMs: null,
      confidence: null,
    };
  });

export const CAPTIONS: Caption[] = [
  ...toCaptions(INTRO_LINES, SCENE_START.intro),
  ...SEGMENT_LINES.flatMap((lines, i) => toCaptions(lines, SCENE_START.segments[i])),
  ...toCaptions(OUTRO_LINES, SCENE_START.outro),
];
