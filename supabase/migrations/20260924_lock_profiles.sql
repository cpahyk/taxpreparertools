-- Review the live schema and back up public.profiles before applying.
-- Existing paid plan values are unverified and must be audited separately.
BEGIN;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Revoke table-level privileges and any older column-level grants. A table-level
-- REVOKE alone does not clear column grants previously given to browser roles.
REVOKE ALL PRIVILEGES ON TABLE public.profiles FROM PUBLIC, anon, authenticated;
DO $revoke_columns$
DECLARE col record;
BEGIN
  FOR col IN SELECT attname FROM pg_attribute
    WHERE attrelid = 'public.profiles'::regclass AND attnum > 0 AND NOT attisdropped
  LOOP
    EXECUTE format('REVOKE SELECT (%1$I), INSERT (%1$I), UPDATE (%1$I), REFERENCES (%1$I) ON TABLE public.profiles FROM PUBLIC, anon, authenticated', col.attname);
  END LOOP;
END
$revoke_columns$;

GRANT SELECT ON TABLE public.profiles TO authenticated;
GRANT INSERT (id, first_name, last_name, email, created_at)
  ON TABLE public.profiles TO authenticated;
GRANT UPDATE (first_name, last_name)
  ON TABLE public.profiles TO authenticated;

-- Restrictive policies intersect any older permissive policies. The permissive
-- policies supply the access path while the restrictive ones enforce ownership.
DROP POLICY IF EXISTS "Users read own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users create own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users edit own profile" ON public.profiles;
DROP POLICY IF EXISTS "Enforce own profile read" ON public.profiles;
DROP POLICY IF EXISTS "Enforce own profile create" ON public.profiles;
DROP POLICY IF EXISTS "Enforce own profile edit" ON public.profiles;
CREATE POLICY "Users read own profile" ON public.profiles
  FOR SELECT TO authenticated USING ((SELECT auth.uid()) = id);
CREATE POLICY "Users create own profile" ON public.profiles
  FOR INSERT TO authenticated WITH CHECK ((SELECT auth.uid()) = id);
CREATE POLICY "Users edit own profile" ON public.profiles
  FOR UPDATE TO authenticated USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);
CREATE POLICY "Enforce own profile read" ON public.profiles AS RESTRICTIVE
  FOR SELECT TO authenticated USING ((SELECT auth.uid()) = id);
CREATE POLICY "Enforce own profile create" ON public.profiles AS RESTRICTIVE
  FOR INSERT TO authenticated WITH CHECK ((SELECT auth.uid()) = id);
CREATE POLICY "Enforce own profile edit" ON public.profiles AS RESTRICTIVE
  FOR UPDATE TO authenticated USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);
COMMIT;
