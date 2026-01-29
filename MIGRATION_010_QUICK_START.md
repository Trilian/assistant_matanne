# QUICK START - Migration 010

## The Problem
PostgreSQL trigger error when updating recipes. Need to add `updated_at` columns.

## The Solution
Run migration 010 to add these columns to your Supabase database.

---

## 3 Steps to Fix

### Step 1: Fix Your Credentials (CRITICAL)
```
File: .env.local
Find: DATABASE_URL=postgresql://postgres.haieczwixbkeuwcgdzvn:...
Note: Your credentials are currently INVALID
Fix:  Get correct string from https://supabase.com/dashboard/ → Settings → Database → Connection Pooling
```

### Step 2: Choose Your Method

**EASIEST: Manual via Web UI**
1. Open: https://supabase.com/dashboard/
2. Go to: SQL Editor
3. Create new query
4. Paste contents of: `sql/010_add_updated_at_columns.sql`
5. Click Run
6. Done!

**OR: Automatic via Python**
```bash
python apply_migration_010_direct.py
```

**OR: Alembic CLI**
```bash
alembic upgrade head
```

### Step 3: Verify It Worked
```bash
python check_migration_status.py
```

Should show:
```
Migration 010 ready to apply:  [YES]
Supabase connection available: [YES]
```

---

## Status Right Now

| Item | Status |
|------|--------|
| Migration scripts ready | ✅ YES |
| SQL script ready | ✅ YES |
| Application tools ready | ✅ YES |
| Supabase credentials | ❌ NO (invalid) |

**Blocker:** Your Supabase credentials are invalid. Fix this first, then apply migration.

---

## Files You Need

- **To apply:** `MIGRATION_010_APPLICATION_GUIDE.md` (detailed guide)
- **To apply:** `sql/010_add_updated_at_columns.sql` (SQL script)
- **To verify:** `check_migration_status.py` (checker)
- **To auto-apply:** `apply_migration_010_direct.py` (if Python preferred)

---

## Troubleshooting

**Q: Where do I get the new DATABASE_URL?**
A: https://supabase.com/dashboard/ → Your project → Settings → Database → Connection Pooling (copy the Pooler connection string)

**Q: Can I use manual SQL instead?**
A: Yes! That's actually the easiest method. See Step 2 above.

**Q: What if I want to work locally first?**
A: Set `DATABASE_URL=sqlite:///./test.db` in `.env.local` temporarily. Apply migration to Supabase later.

**Q: How long does this take?**
A: ~10 minutes once you have the correct credentials.

---

**Everything is ready. You just need to fix your Supabase credentials in `.env.local` and pick your application method above.**
