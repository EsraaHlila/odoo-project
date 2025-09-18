// sync_companies.js
import fetch from "node-fetch";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";
import path from "path";

// Load a custom .env file
dotenv.config({ path: path.resolve('./.env.sync') });

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

const ODOO_HOST = process.env.ODOO_HOST;
const ODOO_DB = process.env.ODOO_DB;
const ODOO_USER = process.env.ODOO_USER;
const ODOO_API_KEY = process.env.ODOO_API_KEY;

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

// Map Supabase row to your unique.company fields
function mapCompanyRow(row) {
  return {
	name: row.name || "Unnamed",
    owner: row.owner || "Unknown owner",
    code: row.code || null, // Unique code
    last_activity_date: row.last_activity_date || null,
    lead_state: row.lead_state || null
  };
}

async function syncCompanies() {
  console.log("Sync started");

  const uid = await odooAuthenticate();
  console.log("Authenticated with UID:", uid);

  const { data, error } = await supabase.from("companies").select("*");
  if (error) throw new Error("Supabase fetch error: " + error.message);

  if (!data || data.length === 0) {
    console.log("No companies found in Supabase.");
    return;
  }

  for (const row of data) {
    if (!row.code) {
      console.log(`Skipping company with no code: ${row.owner}`);
      continue;
    }

    const odooVals = mapCompanyRow(row);

    // Search by code field in your custom model
    const ids = await odooCallObject(uid, "unique.company", "search", [
      [["code", "=", row.code]],
      0,
      1
    ]);

    if (ids.length > 0) {
      await odooCallObject(uid, "unique.company", "write", [[ids[0]], odooVals]);
      console.log(`Updated company ${row.code}`);
    } else {
      await odooCallObject(uid, "unique.company", "create", [odooVals]);
      console.log(`Created company ${row.code}`);
    }
  }
}

syncCompanies().catch((err) => console.error("Fatal sync error:", err));
