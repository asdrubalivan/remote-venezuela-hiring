import type { ReactNode } from "react";
import { fontFamily } from "../fonts";

export const INK = "#f4f4f5";
export const MUTED = "#a1a1aa";
export const STAGE = "#0f1013";

const CHROME_H = 40;

export const BrowserFrame: React.FC<{
  width: number;
  viewportHeight: number;
  url?: string;
  children: ReactNode;
}> = ({ width, viewportHeight, url = "contrataenve.com", children }) => {
  return (
    <div
      style={{
        width,
        height: viewportHeight + CHROME_H,
        borderRadius: 14,
        overflow: "hidden",
        background: "#1c1d22",
        boxShadow: "0 30px 80px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.07)",
      }}
    >
      <div
        style={{
          height: CHROME_H,
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 8,
          position: "relative",
        }}
      >
        {[0, 1, 2].map((i) => (
          <span key={i} style={{ width: 12, height: 12, borderRadius: 6, background: "#3a3c43" }} />
        ))}
        <div
          style={{
            position: "absolute",
            left: "50%",
            transform: "translateX(-50%)",
            height: 26,
            padding: "0 18px",
            borderRadius: 13,
            background: "#2a2c32",
            color: MUTED,
            fontFamily,
            fontSize: 15,
            display: "flex",
            alignItems: "center",
          }}
        >
          {url}
        </div>
      </div>
      <div style={{ width, height: viewportHeight, overflow: "hidden", position: "relative", background: "#fff" }}>
        {children}
      </div>
    </div>
  );
};

export const PhoneFrame: React.FC<{ screenWidth: number; screenHeight: number; children: ReactNode }> = ({
  screenWidth,
  screenHeight,
  children,
}) => {
  const bezel = 11;
  return (
    <div
      style={{
        width: screenWidth + bezel * 2,
        height: screenHeight + bezel * 2,
        borderRadius: 50,
        background: "#050506",
        padding: bezel,
        boxShadow: "0 30px 80px rgba(0,0,0,0.55), 0 0 0 2px #2b2d33",
      }}
    >
      <div
        style={{
          width: screenWidth,
          height: screenHeight,
          borderRadius: 40,
          overflow: "hidden",
          position: "relative",
          background: "#fff",
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const Cursor: React.FC<{ x: number; y: number; pressed: number; opacity: number }> = ({
  x,
  y,
  pressed,
  opacity,
}) => {
  return (
    <svg
      width={34}
      height={34}
      viewBox="0 0 24 24"
      style={{
        position: "absolute",
        left: x - 6,
        top: y - 3,
        opacity,
        transform: `scale(${1 - pressed * 0.18})`,
        transformOrigin: "6px 3px",
        filter: "drop-shadow(0 3px 6px rgba(0,0,0,0.35))",
      }}
    >
      <path d="M5 2.5 L5 19.5 L9.6 15.3 L12.6 21.6 L15.4 20.3 L12.5 14.2 L18.6 14.2 Z" fill="#fff" stroke="#111" strokeWidth={1.4} strokeLinejoin="round" />
    </svg>
  );
};
