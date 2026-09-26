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

// ── companies.json + WebMCP ────────────────────────────────────────────
// `companies.json` is the public dataset contract written by build_site.py;
// the WebMCP tools in webmcp.ts read it and expose it to in-browser agents.

export const COMPANY_FIELDS = [
  "id",
  "name",
  "website",
  "status",
  "last_checked",
  "verification_method",
  "hiring_platform",
  "tags",
  "notes",
  "archived",
] as const;

export type CompanyField = (typeof COMPANY_FIELDS)[number];

export const COMPANY_STATUSES = ["accepts", "rejects", "unknown"] as const;

export const VERIFICATION_METHODS = [
  "application_form",
  "recruiter",
  "public_job_post",
  "community_report",
  "unknown",
] as const;

export const HIRING_PLATFORMS = [
  "greenhouse",
  "ashby",
  "lever",
  "workable",
  "teamtailor",
  "linkedin",
  "company_site",
  "other",
  "unknown",
] as const;

export interface CompanyRecord {
  id: string;
  name: string;
  website: string;
  status: Exclude<Status, "all">;
  last_checked: string;
  verification_method: string;
  hiring_platform: string | null;
  tags: string[];
  notes: string | null;
  archived: boolean;
}

export interface CompaniesFile {
  schema_version: number;
  generated_at: string;
  companies: CompanyRecord[];
}

export interface ListCompaniesInput {
  query?: string;
  status?: (typeof COMPANY_STATUSES)[number];
  verification_method?: (typeof VERIFICATION_METHODS)[number];
  hiring_platform?: (typeof HIRING_PLATFORMS)[number];
  tag?: string;
  include_archived?: boolean;
  fields?: CompanyField[];
}

export interface WebMCPToolAnnotations {
  readOnlyHint?: boolean;
  untrustedContentHint?: boolean;
  consequentialHint?: boolean;
}

export interface WebMCPToolResult {
  content: Array<{ type: "text"; text: string }>;
}

export interface WebMCPTool<Input> {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  annotations?: WebMCPToolAnnotations;
  execute(input: Input): Promise<WebMCPToolResult>;
}

export interface ModelContext {
  registerTool(tool: WebMCPTool<never>): Promise<unknown> | undefined;
}

declare global {
  interface Window {
    RVH?: RVHNamespace;
  }
  interface Document {
    modelContext?: ModelContext;
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
