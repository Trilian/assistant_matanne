# Migration 010 - Application Guide

## Current Status

✅ **Migration 010 is ready to apply**  
❌ **Supabase credentials are invalid**  
   - Error: "Tenant or user not found"  
   - This prevents applying the migration to production

## What is Migration 010?

Migration 010 adds the `updated_at` column to two database tables:
- `recettes` (recipes)
- `modeles_courses` (shopping list models)

**Why?** The PostgreSQL trigger expects these columns but they don't exist, causing errors when updating recipes.

## Your SQLAlchemy models already expect these columns

In `src/core/models/recettes.py` and `src/core/models/courses.py`, the models include:
```python
updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

The migration will synchronize the database schema with your Python models.

---

## How to Apply Migration 010

### **OPTION 1: Fix Supabase Credentials (RECOMMENDED)**

This is the proper fix to ensure production works:

1. **Verify your credentials are correct:**
   - Go to: https://supabase.com/dashboard/
   - Open your project 'assistant-matanne'
   - Navigate to: Settings → Database → Connection Pooling
   - Copy the connection string from the "Pooler" tab (port 6543)
   - It should look like: `postgresql://postgres.xxxxxx:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres`

2. **Update `.env.local`:**
   ```dotenv
   DATABASE_URL=postgresql://postgres.xxxxxx:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```

3. **Test the connection:**
   ```bash
   python check_migration_status.py
   ```
   Should show: `Supabase connection available: [YES]`

4. **Apply the migration:**
   ```bash
   python apply_migration_010_direct.py
   ```

---

### **OPTION 2: Manual Application via Supabase Dashboard**

If you prefer to apply it manually through the web interface:

1. Go to: https://supabase.com/dashboard/project/[your-project-id]/sql/new
2. Create a new SQL query
3. Copy this SQL:

```sql
-- Add updated_at columns to recettes and modeles_courses tables

-- 1. Add updated_at to recettes table
ALTER TABLE recettes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- 2. Add updated_at to modeles_courses table
ALTER TABLE modeles_courses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- 3. Populate updated_at from existing modifie_le for recettes
UPDATE recettes 
SET updated_at = modifie_le 
WHERE updated_at IS NULL AND modifie_le IS NOT NULL;

-- 4. Populate with NOW() for records without modifie_le
UPDATE recettes 
SET updated_at = NOW() 
WHERE updated_at IS NULL;

-- 5. Set NOT NULL constraint for recettes (after population)
ALTER TABLE recettes 
ALTER COLUMN updated_at SET NOT NULL;

-- 6. Populate updated_at from modifie_le for modeles_courses
UPDATE modeles_courses 
SET updated_at = modifie_le 
WHERE updated_at IS NULL AND modifie_le IS NOT NULL;

-- 7. Populate with NOW() for records without modifie_le
UPDATE modeles_courses 
SET updated_at = NOW() 
WHERE updated_at IS NULL;

-- 8. Set NOT NULL constraint for modeles_courses (after population)
ALTER TABLE modeles_courses 
ALTER COLUMN updated_at SET NOT NULL;
```

4. Click "Run"
5. Verify success in the SQL output

---

### **OPTION 3: Use Alembic CLI (Once credentials are fixed)**

```bash
# List pending migrations
alembic history

# Apply all pending migrations (including 010)
alembic upgrade head

# Check current version
alembic current
```

---

### **OPTION 4: Working with Development SQLite (Temporary)**

If you want to work locally while Supabase credentials are being fixed:

```python
# Temporary workaround for development
# Set in your .env.local:
DATABASE_URL=sqlite:///./test.db

# Then the app will use local SQLite database
# When Supabase is ready, change back and apply migration 010
```

---

## Verification Steps

### After applying migration, verify it worked:

**1. Check via SQL query in Supabase:**
```sql
-- Check if columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'recettes' AND column_name = 'updated_at';
```

Should return: `updated_at | timestamp with time zone`

**2. Run the verification script:**
```bash
python test_migration_010.py
```

**3. Test the app:**
```bash
streamlit run src/app.py
```

---

## Troubleshooting

### **Error: "Tenant or user not found"**
- Your Supabase credentials are invalid or expired
- Solution: Regenerate credentials in Supabase dashboard

### **Error: "invalid connection option timeout"**
- The connection string format is incorrect
- Solution: Use the exact format from Supabase dashboard

### **Error: "column already exists"**
- The migration was already applied successfully
- Solution: Verify with the SQL query above; no action needed

### **App still works without the migration?**
- Yes! Your SQLAlchemy models are flexible with nullable columns
- The migration just adds the actual columns to match the schema
- Good for development, but needed for production

---

## Timeline

1. ✅ Migration 010 created and tested
2. ✅ SQLAlchemy models updated
3. ✅ SQL script prepared
4. ⏳ **YOU ARE HERE**: Awaiting Supabase credentials fix
5. ⏰ Apply migration 010
6. ⏰ Verify in production
7. ⏰ Update models to set NOT NULL constraints

---

## Files Related to Migration 010

- **Migration script:** `alembic/versions/010_fix_trigger_modifie_le.py`
- **SQL script:** `sql/010_add_updated_at_columns.sql`
- **Application script:** `apply_migration_010_direct.py`
- **Verification script:** `test_migration_010.py`
- **Status checker:** `check_migration_status.py`
- **Models:** 
  - `src/core/models/recettes.py` (has updated_at)
  - `src/core/models/courses.py` (has updated_at)

---

## Next Steps

1. **Verify your Supabase credentials** are correct
2. **Update .env.local** with the correct DATABASE_URL
3. **Run:** `python check_migration_status.py` (should show all YES)
4. **Apply migration:** Choose OPTION 1, 2, or 3 above
5. **Verify success:** Run verification commands

That's it! The migration will be applied and your app will be fully compatible with the new schema.
