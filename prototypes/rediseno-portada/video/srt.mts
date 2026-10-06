// PROTOTIPO — exporta los subtítulos como .srt (X permite adjuntarlos al subir el video).
import { writeFileSync, mkdirSync } from "node:fs";
import { CAPTIONS } from "./src/timeline.ts";

const ts = (ms: number) => {
  const h = String(Math.floor(ms / 3600000)).padStart(2, "0");
  const m = String(Math.floor((ms % 3600000) / 60000)).padStart(2, "0");
  const s = String(Math.floor((ms % 60000) / 1000)).padStart(2, "0");
  const r = String(ms % 1000).padStart(3, "0");
  return `${h}:${m}:${s},${r}`;
};

const body = CAPTIONS.map((c, i) => `${i + 1}\n${ts(c.startMs)} --> ${ts(c.endMs)}\n${c.text}\n`).join("\n");
mkdirSync("out", { recursive: true });
writeFileSync("out/subtitulos-es.srt", body);
console.log(`out/subtitulos-es.srt (${CAPTIONS.length} líneas)`);
