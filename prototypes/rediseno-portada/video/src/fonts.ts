import { loadFont } from "@remotion/google-fonts/SchibstedGrotesk";

export const { fontFamily } = loadFont("normal", {
  weights: ["500", "600", "700", "800"],
  subsets: ["latin", "latin-ext"],
});
