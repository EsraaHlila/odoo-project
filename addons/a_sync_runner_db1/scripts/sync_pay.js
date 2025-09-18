// sync_unique_payment.js
console.log("Script started");
console.log("sync_unique_payment.js loaded and running");

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

/** Search in Odoo for a record by code (payment code) */
async function odooFindByCode(uid, codeValue) {
  const { result, error } = await odooCallObject(uid, "unique.payment", "search", [
    [["code", "=", String(codeValue)]],
    0,
  ]);
  if (error) return { error };
  return { ids: result || [] };
}

/** Create record in Odoo. Returns id or null */
async function odooCreate(uid, values) {
  const { result, error } = await odooCallObject(uid, "unique.payment", "create", [
    values,
  ]);
  if (error) {
    return { error };
  }
  return { id: result };
}

/** Update record in Odoo. Returns true/false or error */
async function odooUpdate(uid, id, values) {
  const { result, error } = await odooCallObject(uid, "unique.payment", "write", [
    [id],
    values,
  ]);
  if (error) return { error };
  return { ok: result };
}

/** Normalize a Supabase row to Odoo values */
function mapRowToOdoo(row) {
  return {
    parent_name: row.parent_name || false,
    parent_phone: row.parent_phone || false,
    billing_address: row.billing_address || false,
    payment_type: row.payment_type || false, // expects 'online' or 'cash'
    code: row.code != null ? String(row.code) : undefined,
    amount: typeof row.amount === "number" ? row.amount : 0,
    status: row.status || "draft",
    sale_order_id: row.sale_order_id || false, // optional Many2one ID
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
  const { data: payments, error } = await supabase.from("unique_payment").select("*");

  if (error) {
    console.error("Error fetching from Supabase:", error);
    return;
  }
  if (!payments || payments.length === 0) {
    console.log("No rows to sync.");
    return;
  }
  console.log(`Fetched ${payments.length} rows from Supabase.`);

  for (const payment of payments) {
    try {
      const codeVal = payment.code;
      if (codeVal === null || codeVal === undefined) {
        console.warn("Skipping row without payment code:", payment);
        continue;
      }

      const { ids, error: searchErr } = await odooFindByCode(uid, codeVal);
      if (searchErr) {
        console.error("Error searching Odoo for code", codeVal, searchErr);
        continue;
      }

      const odooValues = mapRowToOdoo(payment);

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

      // small delay to avoid hammering Odoo (optional)
      await new Promise((r) => setTimeout(r, 50));
    } catch (err) {
      console.error("Unexpected error processing row", payment, err);
    }
  }

  console.log("Sync finished:", new Date().toLocaleString());
}

// Directly call the sync function without conditional checks
syncSupabaseToOdoo().catch((e) => console.error("Fatal error in sync:", e));

export { syncSupabaseToOdoo };
