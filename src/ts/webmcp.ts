// webmcp.ts — Exposes the companies dataset to in-browser AI agents through
// WebMCP (`document.modelContext.registerTool`).
//
// The tools are read-only views over the public `companies.json` (written by
// build_site.py), loaded once per page and resolved relative to this script so
// the same bundle works from `/` and from `/company/<id>.html`. Browsers
// without WebMCP are left untouched.

import {
  COMPANY_FIELDS,
  COMPANY_STATUSES,
  HIRING_PLATFORMS,
  VERIFICATION_METHODS,
} from "./contracts";
import type {
  CompaniesFile,
  CompanyField,
  CompanyRecord,
  GetCompanyInput,
  ListCompaniesInput,
  ModelContext,
  WebMCPTool,
  WebMCPToolResult,
} from "./contracts";

(function (): void {
  "use strict";

  const modelContext: ModelContext | undefined = document.modelContext;
  if (!modelContext) return;

  const script = document.currentScript;
  const scriptSrc = script instanceof HTMLScriptElement ? script.src : location.href;
  const DATA_URL = new URL("../companies.json", scriptSrc).href;

  let dataset: Promise<CompaniesFile> | null = null;

  function loadDataset(): Promise<CompaniesFile> {
    if (!dataset) {
      const request = fetch(DATA_URL).then((response) => {
        if (!response.ok) throw new Error(`GET ${DATA_URL} failed: ${response.status}`);
        return response.json() as Promise<CompaniesFile>;
      });
      // Don't cache a failure: let the next tool call retry.
      request.catch(() => {
        dataset = null;
      });
      dataset = request;
    }
    return dataset;
  }

  function project(company: CompanyRecord, fields: readonly CompanyField[]): Partial<CompanyRecord> {
    const wanted = new Set<CompanyField>(fields);
    wanted.add("id");
    const out: Record<string, unknown> = {};
    for (const field of COMPANY_FIELDS) {
      if (wanted.has(field)) out[field] = company[field];
    }
    return out as Partial<CompanyRecord>;
  }

  function textResult(payload: unknown): WebMCPToolResult {
    return { content: [{ type: "text", text: JSON.stringify(payload) }] };
  }

  // Agents can send anything, so enum-like inputs are checked at runtime and a
  // problem is answered as plain text (a thrown error reaches the caller as a
  // bare `null`, which an agent can't act on).
  const ENUM_FILTERS: ReadonlyArray<[string, readonly string[]]> = [
    ["status", COMPANY_STATUSES],
    ["verification_method", VERIFICATION_METHODS],
    ["hiring_platform", HIRING_PLATFORMS],
  ];

  function invalid(name: string, got: unknown, valid: readonly string[]): WebMCPToolResult {
    const text = `Invalid value for "${name}": ${JSON.stringify(got)}. Valid values: ${valid.join(", ")}.`;
    return { content: [{ type: "text", text }] };
  }

  function validate(input: Record<string, unknown>): WebMCPToolResult | null {
    for (const [name, valid] of ENUM_FILTERS) {
      const value = input[name];
      if (value !== undefined && !valid.includes(value as string)) {
        return invalid(name, value, valid);
      }
    }
    const fields = input["fields"];
    if (fields !== undefined) {
      if (!Array.isArray(fields)) return invalid("fields", fields, COMPANY_FIELDS);
      for (const field of fields) {
        if (!COMPANY_FIELDS.includes(field as CompanyField)) {
          return invalid("fields", field, COMPANY_FIELDS);
        }
      }
    }
    return null;
  }

  function matches(company: CompanyRecord, input: ListCompaniesInput): boolean {
    if (company.archived && !input.include_archived) return false;
    if (input.status && company.status !== input.status) return false;
    if (input.verification_method && company.verification_method !== input.verification_method) {
      return false;
    }
    if (input.hiring_platform && company.hiring_platform !== input.hiring_platform) return false;
    if (input.tag && !company.tags.includes(input.tag)) return false;
    const query = input.query?.trim().toLowerCase();
    if (query) {
      // Same haystack as the search box on the index page.
      const haystack = `${company.name} ${company.tags.join(" ")} ${company.notes ?? ""}`;
      if (!haystack.toLowerCase().includes(query)) return false;
    }
    return true;
  }

  const READ_ONLY_UNTRUSTED = { readOnlyHint: true, untrustedContentHint: true } as const;

  const listCompanies: WebMCPTool<ListCompaniesInput> = {
    name: "list_companies",
    description:
      "List companies from the Remote Venezuela Hiring directory: companies that accept or " +
      "reject candidates living in Venezuela. Filters are optional and combined with AND; " +
      "archived companies are excluded unless `include_archived` is true. Each entry has status (accepts, rejects or " +
      "unknown), how it was verified and when. The free-text `notes` field is written in " +
      "Spanish and comes from community contributions. The full list is large: use `fields` " +
      "to request only the fields you need (`id` is always included).",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Case-insensitive text to look for in the name, tags and notes.",
        },
        status: {
          type: "string",
          enum: [...COMPANY_STATUSES],
          description: "Only companies with this stance towards candidates from Venezuela.",
        },
        verification_method: {
          type: "string",
          enum: [...VERIFICATION_METHODS],
          description: "Only companies whose status was verified this way.",
        },
        hiring_platform: {
          type: "string",
          enum: [...HIRING_PLATFORMS],
          description: "Only companies that hire through this platform.",
        },
        tag: { type: "string", description: "Only companies with exactly this tag." },
        include_archived: {
          type: "boolean",
          description: "Also return archived companies. Defaults to false.",
        },
        fields: {
          type: "array",
          items: { type: "string", enum: [...COMPANY_FIELDS] },
          description: "Fields to return for each company. Defaults to all ten fields.",
        },
      },
    },
    annotations: READ_ONLY_UNTRUSTED,
    async execute(input: ListCompaniesInput): Promise<WebMCPToolResult> {
      const problem = validate(input as Record<string, unknown>);
      if (problem) return problem;
      const { companies } = await loadDataset();
      const fields = input.fields ?? COMPANY_FIELDS;
      const visible = companies.filter((company) => matches(company, input));
      return textResult({
        count: visible.length,
        companies: visible.map((company) => project(company, fields)),
      });
    },
  };

  const getCompany: WebMCPTool<GetCompanyInput> = {
    name: "get_company",
    description:
      "Get one company from the Remote Venezuela Hiring directory by its `id` (as returned by " +
      "`list_companies`). Archived companies are found too. The free-text `notes` field is " +
      "written in Spanish and comes from community contributions. Use `fields` to request " +
      "only the fields you need (`id` is always included).",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Company id, e.g. \"toptal\"." },
        fields: {
          type: "array",
          items: { type: "string", enum: [...COMPANY_FIELDS] },
          description: "Fields to return. Defaults to all ten fields.",
        },
      },
      required: ["id"],
    },
    annotations: READ_ONLY_UNTRUSTED,
    async execute(input: GetCompanyInput): Promise<WebMCPToolResult> {
      const problem = validate(input as unknown as Record<string, unknown>);
      if (problem) return problem;
      const id: unknown = input.id;
      if (typeof id !== "string" || id === "") {
        return { content: [{ type: "text", text: 'Missing required "id" (a non-empty string).' }] };
      }
      const { companies } = await loadDataset();
      const company = companies.find((candidate) => candidate.id === id);
      if (!company) {
        const text = `No company with id ${JSON.stringify(id)}. Use list_companies to find valid ids.`;
        return { content: [{ type: "text", text }] };
      }
      return textResult({ company: project(company, input.fields ?? COMPANY_FIELDS) });
    },
  };

  function register(tool: WebMCPTool<never>): void {
    try {
      Promise.resolve(modelContext?.registerTool(tool)).catch((error: unknown) => {
        console.warn(`[webmcp] could not register ${tool.name}:`, error);
      });
    } catch (error) {
      console.warn(`[webmcp] could not register ${tool.name}:`, error);
    }
  }

  register(listCompanies as WebMCPTool<never>);
  register(getCompany as WebMCPTool<never>);
})();
