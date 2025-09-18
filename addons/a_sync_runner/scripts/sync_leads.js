// sync_leads.js
import fetch from "node-fetch";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";
dotenv.config();

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

// Simple function to find UTM record by name
async function findUTMRecord(uid, model, name) {
  if (!name) return null;
  
  try {
    const records = await odooCallObject(uid, model, "search_read", [
      [["name", "=", name]],
      ["id"],
      0,
      1
    ]);
    
    if (records.length > 0) {
      console.log(`DEBUG - Found ${model} ID ${records[0].id} for '${name}'`);
      return records[0].id;
    }
    
    console.log(`DEBUG - No ${model} found for '${name}', will create`);
    return null;
  } catch (error) {
    console.error(`Error finding ${model} for '${name}':`, error.message);
    return null;
  }
}

// Simple function to create UTM record
async function createUTMRecord(uid, model, name) {
  if (!name) return null;
  
  try {
    const newId = await odooCallObject(uid, model, "create", [{ name }]);
    console.log(`DEBUG - Created ${model} '${name}' with ID: ${newId}`);
    return newId;
  } catch (error) {
    console.error(`Error creating ${model} '${name}':`, error.message);
    return null;
  }
}

// Simple function to handle UTM fields (medium, source, campaign)
async function handleUTMField(uid, row, fieldName, model) {
  const value = row[fieldName] || row[`${fieldName}_name`];
  
  if (!value) {
    console.log(`DEBUG - No ${fieldName} value found`);
    return null;
  }
  
  console.log(`DEBUG - Processing ${fieldName}: '${value}'`);
  
  // First try to find existing record
  const existingId = await findUTMRecord(uid, model, value);
  if (existingId) {
    return existingId;
  }
  
  // If not found, create new record
  const newId = await createUTMRecord(uid, model, value);
  return newId;
}

// Map stage based on the 'state' field from Supabase
async function getStageAndType(uid, row) {
  const stageValue = row.state || null;
  const normalizedStage = (stageValue || "").toLowerCase().trim();
  
  console.log(`DEBUG - State value from Supabase: '${stageValue}', normalized: '${normalizedStage}'`);
  
  let targetStage = 'New';
  let type = 'opportunity';
  
  const stageMappings = [
    { keywords: ['qualif', 'qualified', 'qualify'], target: 'Qualified', oppType: 'opportunity' },
    { keywords: ['proposition', 'proposal'], target: 'Proposition', oppType: 'opportunity' },
    { keywords: ['negotiation', 'negotiate'], target: 'Negotiation', oppType: 'opportunity' },
    { keywords: ['won', 'closed won', 'win'], target: 'Won', oppType: 'opportunity' },
    { keywords: ['lost', 'closed lost'], target: 'Lost', oppType: 'opportunity' },
    { keywords: ['new'], target: 'New', oppType: 'opportunity' }
  ];

  if (normalizedStage) {
    let foundMapping = false;
    for (const mapping of stageMappings) {
      if (mapping.keywords.some(keyword => normalizedStage.includes(keyword))) {
        targetStage = mapping.target;
        type = mapping.oppType;
        foundMapping = true;
        console.log(`DEBUG - Mapped '${normalizedStage}' to '${targetStage}' with type '${type}'`);
        break;
      }
    }
    
    if (!foundMapping) {
      console.log(`DEBUG - No specific mapping found for '${normalizedStage}', using default 'New'`);
    }
  } else {
    console.log(`DEBUG - No state value found, using default 'New'`);
  }
  
  // Search for the stage in Odoo
  const stages = await odooCallObject(uid, "crm.stage", "search_read", [
    [["name", "ilike", targetStage]],
    ["id"],
    0,
    1
  ]);

  const stage_id = stages.length > 0 ? stages[0].id : null;
  console.log(`DEBUG - Found stage ID: ${stage_id} for '${targetStage}'`);
  
  return { stage_id, type };
}

async function mapLeadRow(uid, row) {
  const { stage_id, type } = await getStageAndType(uid, row);
  const team_id = await getDefaultTeamId(uid);
  const user_id = await getDefaultSalespersonId(uid);

  // Handle UTM fields
  const [medium_id, source_id, campaign_id] = await Promise.all([
    handleUTMField(uid, row, "medium_id", "utm.medium"),
    handleUTMField(uid, row, "source_id", "utm.source"),
    handleUTMField(uid, row, "campaign_id", "utm.campaign")
  ]);

  // Map all important fields from Supabase to Odoo
  const odooVals = {
    // Basic information
    name: row.name || "Unnamed Lead",
    email_from: row.email || row.email_address || row.contact_email || null,
    phone: row.phone || row.phone_number || row.mobile || row.contact_phone || null,
    
    // Description and notes
    description: row.description || row.notes || row.comments || row.remarks || null,
    
    // Address information
    street: row.street || row.address || row.address_line_1 || null,
    street2: row.street2 || row.address_line_2 || null,
    city: row.city || null,
    zip: row.zip || row.postal_code || null,
    
    // Company information
    partner_name: row.company || row.company_name || row.organization || null,
    function: row.job_title || row.position || row.function || null,
    
    // Source information (Many2one fields)
    ...(medium_id && { medium_id }),
    ...(source_id && { source_id }),
    ...(campaign_id && { campaign_id }),
    
    // Dates
    date_action_last: row.last_action_date || null,
    date_action_next: row.next_action_date || null,
    
    // CRM specific fields
    stage_id: stage_id,
    team_id: team_id,
    type: type,
    user_id: user_id,
    
    // Priority
    priority: row.priority || '1',
    
    // Expected revenue and probability
    expected_revenue: row.expected_revenue || null,
    probability: row.probability || null,
  };

  // Remove null values
  Object.keys(odooVals).forEach(key => {
    if (odooVals[key] === null || odooVals[key] === undefined) {
      delete odooVals[key];
    }
  });

  console.log(`DEBUG - Mapped Odoo values:`, JSON.stringify(odooVals, null, 2));
  
  return odooVals;
}

async function getDefaultTeamId(uid) {
  try {
    const teams = await odooCallObject(uid, "crm.team", "search_read", [
      [],
      ["id"],
      0,
      1
    ]);
    return teams.length > 0 ? teams[0].id : null;
  } catch (error) {
    console.warn("Could not get default team:", error.message);
    return null;
  }
}

async function getDefaultSalespersonId(uid) {
  try {
    const users = await odooCallObject(uid, "res.users", "search_read", [
      [],
      ["id"],
      0,
      1
    ]);
    return users.length > 0 ? users[0].id : null;
  } catch (error) {
    console.warn("Could not get default salesperson:", error.message);
    return null;
  }
}

// Debug function to see what fields are available in Supabase
async function debugSupabaseFields() {
  try {
    const { data, error } = await supabase.from("leads").select("*").limit(1);
    if (error) throw error;
    
    if (data && data.length > 0) {
      console.log("DEBUG - Available fields in Supabase leads:", Object.keys(data[0]));
      console.log("DEBUG - Sample data:", JSON.stringify(data[0], null, 2));
    }
  } catch (error) {
    console.error("DEBUG - Could not fetch Supabase structure:", error.message);
  }
}

async function syncLeads() {
  console.log("Lead sync started");

  const uid = await odooAuthenticate();
  console.log("Authenticated with UID:", uid);

  // Debug: Check what fields are available in Supabase
  await debugSupabaseFields();

  // Select all fields from Supabase
  const { data, error } = await supabase.from("leads").select("*");
  if (error) throw new Error("Supabase fetch error: " + error.message);

  if (!data || data.length === 0) {
    console.log("No leads found in Supabase.");
    return;
  }

  for (const row of data) {
    try {
      if (!row.name) {
        console.log(`Skipping lead with no name`);
        continue;
      }

      console.log(`\nProcessing: ${row.name}`);
      
      const odooVals = await mapLeadRow(uid, row);

      // Search by multiple criteria
      const domain = [];
      if (row.email) {
        domain.push(["email_from", "=", row.email]);
      }
      if (row.phone) {
        domain.push(["phone", "=", row.phone]);
      }
      if (row.name) {
        domain.push(["name", "=", row.name]);
      }

      const ids = await odooCallObject(uid, "crm.lead", "search", [
        domain.length > 0 ? domain : [],
        0,
        1
      ]);

      if (ids.length > 0) {
        await odooCallObject(uid, "crm.lead", "write", [[ids[0]], odooVals]);
        console.log(`✓ Updated ${odooVals.type} '${row.name}'`);
      } else {
        const newId = await odooCallObject(uid, "crm.lead", "create", [odooVals]);
        console.log(`✓ Created ${odooVals.type} '${row.name}' with ID: ${newId}`);
      }
    } catch (err) {
      console.error(`✗ Error processing ${row.name}:`, err.message);
    }
  }
}

syncLeads().catch((err) => console.error("Fatal sync error:", err));