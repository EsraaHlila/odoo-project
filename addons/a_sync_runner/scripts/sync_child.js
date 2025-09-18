// sync_child.js
console.log("Script started");
console.log("sync_child.js loaded and running");

import fetch from "node-fetch";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";
dotenv.config();

// CONFIG from .env
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;

const ODOO_HOST = process.env.ODOO_HOST || "http://localhost:8069";
const ODOO_DB = process.env.ODOO_DB;
const ODOO_USER = process.env.ODOO_USER;
const ODOO_API_KEY = process.env.ODOO_API_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.error("Supabase config missing in .env");
  process.exit(1);
} else {
  console.log("Supabase config loaded");
}
if (!ODOO_DB || !ODOO_USER || !ODOO_API_KEY) {
  console.error("Odoo config missing in .env");
  process.exit(1);
} else {
  console.log("Odoo config loaded");
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

/** Helper: map gender values from Supabase to Odoo selection values */
function mapGender(val) {
  if (val === null || val === undefined) return null;
  const v = String(val).trim().toLowerCase();
  if (["m", "male"].includes(v)) return "male";
  if (["f", "female"].includes(v)) return "female";
  return v || null;
}

/** Authenticate to Odoo (returns uid) */
async function odooAuthenticate() {
  try {
    const res = await fetch(`${ODOO_HOST}/jsonrpc`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "common",
          method: "authenticate",
          args: [ODOO_DB, ODOO_USER, ODOO_API_KEY, {}],
        },
        id: 1,
      }),
    });
    const data = await res.json();
    if (data.error) {
      console.error("Odoo auth error:", data.error);
      return null;
    }
    return data.result;
  } catch (err) {
    console.error("Failed to authenticate to Odoo:", err);
    return null;
  }
}

/** Generic JSON-RPC object call helper */
async function odooCallObject(uid, model, method, args = []) {
  try {
    const res = await fetch(`${ODOO_HOST}/jsonrpc`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "object",
          method: "execute_kw",
          args: [ODOO_DB, uid, ODOO_API_KEY, model, method, args],
        },
        id: Math.floor(Math.random() * 100000),
      }),
    });
    const data = await res.json();
    if (data.error) return { error: data.error };
    return { result: data.result };
  } catch (err) {
    return { error: err };
  }
}

/** Search in Odoo for a child record by `code` */
async function odooFindChildByCode(uid, codeValue) {
  const { result, error } = await odooCallObject(uid, "unique.child", "search", [
    [["code", "=", String(codeValue)]],
    0,
  ]);
  if (error) return { error };
  return { ids: result || [] };
}

/** Search parentId in Odoo by parent code */
async function odooFindParentId(uid, parentCode) {
  const { result, error } = await odooCallObject(uid, "unique.parent", "search", [
    [["code", "=", parentCode]],
    0,
  ]);
  if (error) return { error };
  return result[0] || null;
}

/** Create child record in Odoo. Returns id or null */
async function odooCreateChild(uid, values) {
  const { result, error } = await odooCallObject(uid, "unique.child", "create", [
    values,
  ]);
  if (error) return { error };
  return { id: result };
}

/** Update child record in Odoo. Returns true/false or error */
async function odooUpdateChild(uid, id, values) {
  const { result, error } = await odooCallObject(uid, "unique.child", "write", [
    [id],
    values,
  ]);
  if (error) return { error };
  return { ok: result };
}

/** Normalize a Supabase row to Odoo child values */
async function mapRowToOdooChild(uid, row) {
  const parentId = await odooFindParentId(uid, row.parentId);
  if (!parentId) {
    console.warn("Parent not found in Odoo for code:", row.parentId);
    return null; // skip this child row
  }

  return {
    first_name: row.firstName || false,
    last_name: row.lastName || false,
    birth_date: row.birthDate || false,
    moyenne: row.moyennes != null ? row.moyennes : 0,
    gender: mapGender(row.gender),
    parent_id: parentId, // ✅ integer ID of parent
	niveauId: row.niveauId,
    code: row.code || undefined,
  };
}

/** Main sync logic */
async function syncSupabaseToOdooChild() {
  console.log("Starting child sync:", new Date().toLocaleString());

  const uid = await odooAuthenticate();
  if (!uid) {
    console.error("Failed to authenticate to Odoo - aborting sync");
    return;
  }
  console.log("Authenticated to Odoo with UID:", uid);

  // fetch from Supabase
  const { data: children, error } = await supabase
    .from("unique_child")
    .select("*");

  if (error) {
    console.error("Error fetching from Supabase:", error);
    return;
  }
  if (!children || children.length === 0) {
    console.log("No child rows to sync.");
    return;
  }
  console.log(`Fetched ${children.length} child rows from Supabase.`);

  for (const row of children) {
    try {
      if (!row.code) {
        console.warn("Skipping child row without code:", row);
        continue;
      }

      const odooValues = await mapRowToOdooChild(uid, row);
      if (!odooValues) continue; // parent not found

      const { ids, error: searchErr } = await odooFindChildByCode(uid, row.code);
      if (searchErr) {
        console.error("Error searching Odoo for child code", row.code, searchErr);
        continue;
      }

      if (ids && ids.length > 0) {
        const id = ids[0];
        const { error: updErr } = await odooUpdateChild(uid, id, odooValues);
        if (updErr) console.error("Odoo update error for code", row.code, updErr);
        else console.log(`Updated Odoo child id=${id} for code=${row.code}`);
      } else {
        const { id, error: createErr } = await odooCreateChild(uid, odooValues);
        if (createErr) console.error("Odoo create error for code", row.code, createErr);
        else console.log(`Created Odoo child id=${id} for code=${row.code}`);
      }

      await new Promise((r) => setTimeout(r, 50));
    } catch (err) {
      console.error("Unexpected error processing child row", row, err);
    }
  }

  console.log("Child sync finished:", new Date().toLocaleString());
}

// Run immediately
syncSupabaseToOdooChild().catch((e) =>
  console.error("Fatal error in child sync:", e)
);

export { syncSupabaseToOdooChild };
