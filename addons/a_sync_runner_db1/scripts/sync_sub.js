// sync.js
console.log("Script started")
console.log("sync.js loaded and running");

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
  // adjust fallback to what your Odoo selection accepts
  return v || "other";
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

/** Search in Odoo for a record by ref (subs_reference) */
async function odooFindByRef(uid, refValue) {
  // Odoo expects the comparison value to be string (ref is char)
  const searchDomain = [[["ref", "=", String(refValue)]]]; // note double nesting for execute_kw
  const { result, error } = await odooCallObject(uid, "unique.subscription", "search", [
    [["ref", "=", String(refValue)]],
    0,
  ]);
  if (error) return { error };
  return { ids: result || [] };
}

/** Create record in Odoo. Returns id or null */
async function odooCreate(uid, values) {
  const { result, error } = await odooCallObject(uid, "unique.subscription", "create", [
    values,
  ]);
  if (error) {
    return { error };
  }
  return { id: result };
}

/** Update record in Odoo. Returns true/false or error */
async function odooUpdate(uid, id, values) {
  const { result, error } = await odooCallObject(uid, "unique.subscription", "write", [
    [id],
    values,
  ]);
  if (error) return { error };
  return { ok: result };
}

/** Normalize a Supabase row to Odoo values */
function mapRowToOdoo(sub) {
  return {
    // ref in Odoo is a char field, convert subs_reference to string
    ref: sub.subs_reference != null ? String(sub.subs_reference) : undefined,
    parent_first_name: sub.parent_first_name || false,
    parent_last_name: sub.parent_last_name || false,
    birth_date: sub.parent_birth_date || false, // expect 'YYYY-MM-DD'
    gender: mapGender(sub.parent_gender),
    child_first_name: sub.child_first_name || false,
    child_last_name: sub.child_last_name || false,
    child_birth_date: sub.child_birth_date || false,
    child_gender: mapGender(sub.child_gender),
    activee: sub.is_active === null || sub.is_active === undefined ? true : !!sub.is_active,
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
  const { data: subs, error } = await supabase
    .from("unique_subscription")
    .select("*");

  if (error) {
    console.error("Error fetching from Supabase:", error);
    return;
  }
  if (!subs || subs.length === 0) {
    console.log("No rows to sync.");
    return;
  }
  console.log(`Fetched ${subs.length} rows from Supabase.`);

  for (const sub of subs) {
    try {
      // required linking value
      const linkVal = sub.subs_reference;
      if (linkVal === null || linkVal === undefined) {
        console.warn("Skipping row without subs_reference:", sub);
        continue;
      }

      // search by ref
      const { ids, error: searchErr } = await odooFindByRef(uid, linkVal);
      if (searchErr) {
        console.error("Error searching Odoo for ref", linkVal, searchErr);
        continue;
      }

      const odooValues = mapRowToOdoo(sub);

      if (ids && ids.length > 0) {
        // update first match
        const id = ids[0];
        const { error: updErr, ok } = await odooUpdate(uid, id, odooValues);
        if (updErr) {
          console.error("Odoo update error for ref", linkVal, updErr);
        } else {
          console.log(`Updated Odoo record id=${id} for ref=${linkVal}`);
        }
      } else {
        // create
        const { id, error: createErr } = await odooCreate(uid, odooValues);
        if (createErr) {
          console.error("Odoo create error for ref", linkVal, createErr);
        } else {
          console.log(`Created Odoo record id=${id} for ref=${linkVal}`);
        }
      }
      // small delay to avoid hammering Odoo (optional)
      await new Promise((r) => setTimeout(r, 50));
    } catch (err) {
      console.error("Unexpected error processing row", sub, err);
    }
  }

  console.log("Sync finished:", new Date().toLocaleString());
}

/** If script is invoked directly, run sync */

// Directly call the sync function without conditional checks
syncSupabaseToOdoo().catch((e) => console.error("Fatal error in sync:", e));

if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith("sync.js")) {
  syncSupabaseToOdoo().catch((e) => console.error("Fatal error in sync:", e));
}

export { syncSupabaseToOdoo };
