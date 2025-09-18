// sync_unique_package.js
console.log("Script started");
console.log("sync_unique_package.js loaded and running");

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
}
if (!ODOO_DB || !ODOO_USER || !ODOO_API_KEY) {
  console.error("Odoo config missing in .env");
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

/** Authenticate to Odoo (returns uid) */
async function odooAuthenticate() {
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
}

/** Generic JSON-RPC object call helper */
async function odooCallObject(uid, model, method, args = []) {
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
}

/** Search in Odoo for a record by code */
async function odooFindByCode(uid, codeValue) {
  const { result, error } = await odooCallObject(uid, "unique.package", "search", [
    [["code", "=", String(codeValue)]],
    0,
  ]);
  if (error) return { error };
  return { ids: result || [] };
}

/** Create record in Odoo */
async function odooCreate(uid, values) {
  const { result, error } = await odooCallObject(uid, "unique.package", "create", [values]);
  if (error) return { error };
  return { id: result };
}

/** Update record in Odoo */
async function odooUpdate(uid, id, values) {
  const { result, error } = await odooCallObject(uid, "unique.package", "write", [[id], values]);
  if (error) return { error };
  return { ok: result };
}

/** Map Supabase row to Odoo values */
function mapRowToOdoo(row) {
  return {
    name: row.name || "Unnamed Package",
    price: typeof row.price === "number" ? row.price : 0,
    validation_days: typeof row.ValidationDays === "number" ? row.ValidationDays : 0,
    description: row.description || "",
    code: row.id != null ? String(row.id) : undefined, // using Supabase id as code
  };
}

/** Main sync logic */
async function syncSupabaseToOdoo() {
  console.log("Starting sync:", new Date().toLocaleString());

  const uid = await odooAuthenticate();
  if (!uid) {
    console.error("Failed to authenticate to Odoo - aborting sync");
    return;
  }
  console.log("Authenticated to Odoo with UID:", uid);

  // fetch from Supabase
  const { data: packages, error } = await supabase.from("package").select("*");
  if (error) {
    console.error("Error fetching from Supabase:", error);
    return;
  }
  if (!packages || packages.length === 0) {
    console.log("No rows to sync.");
    return;
  }
  console.log(`Fetched ${packages.length} rows from Supabase.`);

  for (const pkg of packages) {
    try {
      const codeVal = pkg.id;
      if (codeVal === null || codeVal === undefined) {
        console.warn("Skipping row without ID:", pkg);
        continue;
      }

      const { ids, error: searchErr } = await odooFindByCode(uid, codeVal);
      if (searchErr) {
        console.error("Error searching Odoo for code", codeVal, searchErr);
        continue;
      }

      const odooValues = mapRowToOdoo(pkg);

      if (ids && ids.length > 0) {
        const id = ids[0];
        const { error: updErr, ok } = await odooUpdate(uid, id, odooValues);
        if (updErr) {
          console.error("Odoo update error for code", codeVal, updErr);
        } else {
          console.log(`Updated Odoo record id=${id} for code=${codeVal}`);
        }
      } else {
        const { id, error: createErr } = await odooCreate(uid, odooValues);
        if (createErr) {
          console.error("Odoo create error for code", codeVal, createErr);
        } else {
          console.log(`Created Odoo record id=${id} for code=${codeVal}`);
        }
      }

      await new Promise((r) => setTimeout(r, 50)); // optional delay
    } catch (err) {
      console.error("Unexpected error processing row", pkg, err);
    }
  }

  console.log("Sync finished:", new Date().toLocaleString());
}

// Run directly
syncSupabaseToOdoo().catch((e) => console.error("Fatal error in sync:", e));

export { syncSupabaseToOdoo };
