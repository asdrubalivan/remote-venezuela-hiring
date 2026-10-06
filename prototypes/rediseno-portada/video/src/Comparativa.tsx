// PROTOTIPO — video comparativo de las 5 variantes de la portada, para X.
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { Fragment } from "react";
import { AbsoluteFill, Easing } from "remotion";
import { Subtitles } from "./components/Subtitles";
import { STAGE } from "./components/Frames";
import { Intro, Outro, Segment } from "./scenes";
import { CAPTIONS, INTRO, OUTRO, SEGMENT, TRANSITION, VARIANTS } from "./timeline";

const timing = linearTiming({ durationInFrames: TRANSITION, easing: Easing.bezier(0.65, 0, 0.35, 1) });

export const Comparativa: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: STAGE }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={INTRO}>
          <Intro />
        </TransitionSeries.Sequence>
        {VARIANTS.map((v) => (
          <Fragment key={v.n}>
            <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />
            <TransitionSeries.Sequence durationInFrames={SEGMENT}>
              <Segment v={v} />
            </TransitionSeries.Sequence>
          </Fragment>
        ))}
        <TransitionSeries.Transition presentation={fade()} timing={timing} />
        <TransitionSeries.Sequence durationInFrames={OUTRO}>
          <Outro />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Subtitles captions={CAPTIONS} />
    </AbsoluteFill>
  );
};
