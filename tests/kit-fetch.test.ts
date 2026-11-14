import { afterEach, describe, expect, it, vi } from "vitest";

/**
 * The shared kit finds a plugin's routes on a registry install (generated id) and a local install
 * (its name), and still works on a plain-HTTP page, where browsers give no crypto.subtle (issue #9).
 */
const PLUGIN = "listora";
// The id EmDash gives this slug on every registry install (Wbcom's publisher DID + slug).
const REGISTRY_ID = "r_2oeji6rfeg7ovdex";

const missing = () => new Response(JSON.stringify({ success: false, error: { code: "NOT_FOUND", message: "Plugin route not found" } }), { status: 404 });
const ok = () => new Response(JSON.stringify({ success: true, data: { ok: true } }), { status: 200 });

async function kit() {
	vi.resetModules();
	return import("../site-kit/lib/wbcom-kit");
}

afterEach(() => vi.unstubAllGlobals());

describe("pluginFetch", () => {
	it("works out the registry id the way EmDash does", async () => {
		expect(await (await kit()).registryPluginId(PLUGIN)).toBe(REGISTRY_ID);
	});

	it("tries the registry id, then the name", async () => {
		vi.stubGlobal("window", {});
		const { pluginFetch } = await kit();
		const seen: string[] = [];
		vi.stubGlobal("fetch", async (url: string) => (seen.push(url), url.includes(`/${PLUGIN}/`) ? ok() : missing()));
		expect((await pluginFetch(PLUGIN, "health")).status).toBe(200);
		expect(seen).toEqual([`/_emdash/api/plugins/${REGISTRY_ID}/health`, `/_emdash/api/plugins/${PLUGIN}/health`]);
	});

	it("on a plain-HTTP page (no crypto.subtle) asks the name instead of failing", async () => {
		vi.stubGlobal("window", {});
		vi.stubGlobal("crypto", {});
		const { pluginFetch, api } = await kit();
		const seen: string[] = [];
		vi.stubGlobal("fetch", async (url: string) => (seen.push(url), url.includes(`/${PLUGIN}/`) ? ok() : missing()));
		expect((await pluginFetch(PLUGIN, "health")).status).toBe(200);
		expect(seen).toEqual([`/_emdash/api/plugins/${PLUGIN}/health`]);
		vi.resetModules();
		expect(await api(PLUGIN, "health")).toMatchObject({ ok: true });
	});
});
