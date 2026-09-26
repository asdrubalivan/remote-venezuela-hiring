// webmcp.ts — Exposes the companies dataset to in-browser AI agents through
// WebMCP (`document.modelContext.registerTool`).
//
// The tools are read-only views over the public `companies.json` (written by
// build_site.py), loaded once per page and resolved relative to this script so
// the same bundle works from `/` and from `/company/<id>.html`. Browsers
// without WebMCP are left untouched.

import { COMPANY_FIELDS } from "./contracts";
import type {
  CompaniesFile,
  CompanyField,
  CompanyRecord,
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

  const READ_ONLY_UNTRUSTED = { readOnlyHint: true, untrustedContentHint: true } as const;

  const listCompanies: WebMCPTool<ListCompaniesInput> = {
    name: "list_companies",
    description:
      "List companies from the Remote Venezuela Hiring directory: companies that accept or " +
      "reject candidates living in Venezuela. Each entry has status (accepts, rejects or " +
      "unknown), how it was verified and when. The free-text `notes` field is written in " +
      "Spanish and comes from community contributions. The full list is large: use `fields` " +
      "to request only the fields you need (`id` is always included).",
    inputSchema: {
      type: "object",
      properties: {
        fields: {
          type: "array",
          items: { type: "string", enum: [...COMPANY_FIELDS] },
          description: "Fields to return for each company. Defaults to all ten fields.",
        },
      },
    },
    annotations: READ_ONLY_UNTRUSTED,
    async execute(input: ListCompaniesInput): Promise<WebMCPToolResult> {
      const { companies } = await loadDataset();
      const fields = input.fields ?? COMPANY_FIELDS;
      const visible = companies.filter((company) => !company.archived);
      return textResult({
        count: visible.length,
        companies: visible.map((company) => project(company, fields)),
      });
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
})();
