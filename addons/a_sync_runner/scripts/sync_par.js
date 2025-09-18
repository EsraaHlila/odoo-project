// sync_parent.js
console.log("Script started");
console.log("sync_parent.js loaded and running");

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

/** Search in Odoo for a record by `supabase_id` */
async function odooFindBySupabaseId(uid, supabaseId) {
  const { result, error } = await odooCallObject(uid, "unique.parent", "search", [
    [["supabase_id", "=", supabaseId]],
    0,
  ]);
  if (error) return { error };
  return { ids: result || [] };
}

/** Create record in Odoo. Returns id or null */
async function odooCreate(uid, values) {
  const { result, error } = await odooCallObject(uid, "unique.parent", "create", [
    values,
  ]);
  if (error) return { error };
  return { id: result };
}

/** Update record in Odoo. Returns true/false or error */
async function odooUpdate(uid, id, values) {
  const { result, error } = await odooCallObject(uid, "unique.parent", "write", [
    [id],
    values,
  ]);
  if (error) return { error };
  return { ok: result };
}

/** Map Supabase row to Odoo parent fields */
function mapRowToOdooParent(row, phoneNumber,email) {
  return {
    first_name: row.firstName || false,
    last_name: row.lastName || false,
    birth_date: row.birthDate || false,
    address: row.address || false,
    children_count: row.childrenNumber != null ? row.children_count : 0,
    gender: mapGender(row.sexe),
    activee: row.active === null || row.active === undefined ? true : !!row.active,
    supabase_id: row.id,  // store Supabase ID in Odoo
    phone: phoneNumber || false,	// phone from auth table
	email: email || false,
  };
}

/** Main sync logic */
async function syncSupabaseToOdooParent() {
  console.log("Starting parent sync:", new Date().toLocaleString());

  const uid = await odooAuthenticate();
  if (!uid) {
    console.error("Failed to authenticate to Odoo - aborting sync");
    return;
  }
  console.log("Authenticated to Odoo with UID:", uid);

  // fetch parents from Supabase
  const { data: parents, error: parentError } = await supabase
    .from("unique_parent")
    .select("*");

  if (parentError) {
    console.error("Error fetching parents from Supabase:", parentError);
    return;
  }
  if (!parents || parents.length === 0) {
    console.log("No parent rows to sync.");
    return;
  }

  console.log(`Fetched ${parents.length} parent rows from Supabase.`);

  for (const parent of parents) {
    try {
      if (!parent.id) {
        console.warn("Skipping parent without id:", parent);
        continue;
      }

      // fetch corresponding phone from auth table
      const { data: authData, error: authError } = await supabase
        .from("auth")
        .select("phone,email")
        .eq("id", parent.id)
        .maybeSingle();

      if (authError) {
        console.error("Error fetching phone from auth table for id", parent.id, authError);
        continue;
      }

      const phoneNumber = authData ? authData.phone : null;
	  const email = authData ? authData.email : null;

      const { ids, error: searchErr } = await odooFindBySupabaseId(uid, parent.id);
      if (searchErr) {
        console.error("Error searching Odoo for supabase_id", parent.id, searchErr);
        continue;
      }

      const odooValues = mapRowToOdooParent(parent, phoneNumber,email);
	  //const odooValuess = mapRowToOdooParent(parent, email);

      if (ids && ids.length > 0) {
        const id = ids[0];
        const { error: updErr } = await odooUpdate(uid, id, odooValues);
        if (updErr) {
          console.error("Odoo update error for supabase_id", parent.id, updErr);
        } else {
          console.log(`Updated Odoo parent id=${id} for supabase_id=${parent.id}`);
        }
      } else {
        const { id, error: createErr } = await odooCreate(uid, odooValues);
        if (createErr) {
          console.error("Odoo create error for supabase_id", parent.id, createErr);
        } else {
          console.log(`Created Odoo parent id=${id} for supabase_id=${parent.id}`);
        }
      }

      await new Promise((r) => setTimeout(r, 50));
    } catch (err) {
      console.error("Unexpected error processing parent row", parent, err);
    }
  }

  console.log("Parent sync finished:", new Date().toLocaleString());
}

// Run immediately
syncSupabaseToOdooParent().catch((e) =>
  console.error("Fatal error in parent sync:", e)
);

export { syncSupabaseToOdooParent };
