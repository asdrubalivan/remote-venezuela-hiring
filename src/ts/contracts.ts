// contracts.ts — Shared types for the frontend.
//
// Single source of truth for the DOM contract: what statuses exist, what
// actions the reducer accepts, what custom events look like, and what
// `window.RVH` exposes to Playwright. Both filter.ts and theme.ts import
// from here; if any field drifts, `pnpm typecheck` fails in CI.

export type Status = "all" | "accepts" | "rejects" | "unknown";

export type SortKey =
  | "name"
  | "status"
  | "last_checked"
  | "verification_method"
  | "hiring_platform";

export type SortDir = "asc" | "desc";

export interface FilterState {
  search: string;
  status: Status;
  method: string;
  platform: string;
  tag: string;
  archived: boolean;
  sortBy: SortKey;
  sortDir: SortDir;
}

export type FilterPatch = Partial<Pick<FilterState, "method" | "platform" | "tag">>;

export type FilterAction =
  | { type: "SEARCH"; value: string }
  | { type: "FILTER"; patch: FilterPatch }
  | { type: "STATUS"; value: Status }
  | { type: "ARCHIVED"; value: boolean }
  | { type: "SORT"; key: SortKey }
  | { type: "CLEAR" };

export interface FilterAppliedDetail {
  state: FilterState;
  visible: number;
}

// ── Display preferences (theme + density) ──────────────────────────────

export type Theme = "light" | "dark";
export type Density = "comfortable" | "compact";

export interface ThemeChangedDetail {
  theme: Theme;
}

// ── Public API exposed on window.RVH ───────────────────────────────────

export interface FilterAPI {
  getState(): FilterState;
  dispatch(action: FilterAction): void;
  rowCount(): number;
}

export interface ThemeAPI {
  get(): Theme;
  set(theme: Theme): void;
  toggle(): void;
}

export interface DensityAPI {
  get(): Density;
  set(density: Density): void;
}

export interface RVHNamespace {
  filter?: FilterAPI;
  theme?: ThemeAPI;
  density?: DensityAPI;
}

declare global {
  interface Window {
    RVH?: RVHNamespace;
  }
  interface DocumentEventMap {
    "rvh:filter:applied": CustomEvent<FilterAppliedDetail>;
    "rvh:theme:changed": CustomEvent<ThemeChangedDetail>;
  }
}

// ── Runtime validators (narrow strings off the DOM) ────────────────────

const STATUSES: ReadonlySet<Status> = new Set([
  "all",
  "accepts",
  "rejects",
  "unknown",
]);

export function isStatus(value: string | null | undefined): value is Status {
  return value != null && STATUSES.has(value as Status);
}

const SORT_KEYS: ReadonlySet<SortKey> = new Set([
  "name",
  "status",
  "last_checked",
  "verification_method",
  "hiring_platform",
]);

export function isSortKey(value: string | null | undefined): value is SortKey {
  return value != null && SORT_KEYS.has(value as SortKey);
}

export function assertNever(x: never): never {
  throw new Error("Unhandled case: " + JSON.stringify(x));
}
