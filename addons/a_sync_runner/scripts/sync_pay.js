// sync_unique_payment.js
import fetch from "node-fetch";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";
dotenv.config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const ODOO_HOST = process.env.ODOO_HOST || "http://localhost:8069";
const ODOO_DB = process.env.ODOO_DB;
const ODOO_USER = process.env.ODOO_USER;
const ODOO_API_KEY = process.env.ODOO_API_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY || !ODOO_DB || !ODOO_USER || !ODOO_API_KEY) {
  console.error("Missing config in .env");
  process.exit(1);
}

/** Authenticate to Odoo */
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
  if (data.error) throw new Error("Odoo auth error: " + JSON.stringify(data.error));
  return data.result;
}

/** Generic Odoo JSON-RPC call */
async function odooCallObject(uid, model, method, args) {
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
  if (data.error) throw new Error("Odoo call error: " + JSON.stringify(data.error));
  return data.result;
}

/** Find or create package (Many2one) */
async function findOrCreatePackage(uid, packageName) {
  if (!packageName) return null;

  // search existing
  const ids = await odooCallObject(uid, "unique.package", "search", [
    [["name", "=", packageName]],
    0,
    1,
  ]);
  if (ids.length > 0) return ids[0];

  // create new
  const newId = await odooCallObject(uid, "unique.package", "create", [{ name: packageName }]);
  return newId;
}

/** Map Supabase row to Odoo values */
async function mapRowToOdoo(row, uid) {
  const packageId = row.package_id
    ? await findOrCreatePackage(uid, row.package_id)
    : null;

  return {
    parent_name: row.parent_name || false,
    parent_phone: row.parent_phone || false,
    billing_address: row.billing_address || false,
    payment_type: row.payment_type || false,
    code: row.code != null ? String(row.code) : undefined,
    amount: typeof row.amount === "number" ? row.amount : 0,
    status: row.status || "draft",
    discount_code: row.discount_code || false,
    package_id: packageId,
  };
}

/** Search payment by code */
async function odooFindByCode(uid, codeValue) {
  const ids = await odooCallObject(uid, "unique.payment", "search", [
    [["code", "=", String(codeValue)]],
    0,
    1,
  ]);
  return ids.length > 0 ? ids[0] : null;
}

/** Sync Supabase payments to Odoo */
async function syncSupabaseToOdoo() {
  console.log("Sync started");

  const uid = await odooAuthenticate();
  console.log("Authenticated with UID:", uid);

  const { data: payments, error } = await supabase.from("unique_payment").select("*");
  if (error) throw new Error("Supabase fetch error: " + error.message);
  if (!payments || payments.length === 0) return console.log("No payments to sync.");

  for (const row of payments) {
    if (!row.code) {
      console.warn("Skipping row with no code:", row);
      continue;
    }

    const odooValues = await mapRowToOdoo(row, uid);

    const existingId = await odooFindByCode(uid, row.code);
    if (existingId) {
      await odooCallObject(uid, "unique.payment", "write", [[existingId], odooValues]);
      console.log(`Updated payment ${row.code}`);
    } else {
      await odooCallObject(uid, "unique.payment", "create", [odooValues]);
      console.log(`Created payment ${row.code}`);
    }

    await new Promise((r) => setTimeout(r, 50)); // optional delay
  }

  console.log("Sync finished");
}

syncSupabaseToOdoo().catch((err) => console.error("Fatal error:", err));
