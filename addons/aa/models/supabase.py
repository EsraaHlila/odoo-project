from supabase import create_client, Client

url = "https://ekfkmyhqoynscvgknexq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVrZmtteWhxb3luc2N2Z2tuZXhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQyNzMzMywiZXhwIjoyMDcwMDAzMzMzfQ.aJ1vILpTR3MDlKOBV2K1zFeFmGi-kGPAp3OLC6hmS-8"

supabase: Client = create_client(url, key)

# Example: fetch rows from a table
data = supabase.table("subscription").select("*").execute()

print(data.data)
