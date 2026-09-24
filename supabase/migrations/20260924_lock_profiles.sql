-- Apply after reviewing existing profile policies and backing up the table.
-- Paid entitlements must be written only by a trusted payment webhook using a
-- service role. This migration restricts browser roles to ordinary profile data.
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.profiles FROM anon, authenticated;
GRANT SELECT ON TABLE public.profiles TO authenticated;
GRANT INSERT (id, first_name, last_name, email, role, created_at)
  ON TABLE public.profiles TO authenticated;
GRANT UPDATE (first_name, last_name, role)
  ON TABLE public.profiles TO authenticated;

-- Remove existing policies separately if they expose other users' records.
-- A permissive old policy is ORed with these policies, so audit existing ones.
DROP POLICY IF EXISTS "Users read own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users create own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users edit own profile" ON public.profiles;

CREATE POLICY "Users read own profile" ON public.profiles
  FOR SELECT TO authenticated USING ((SELECT auth.uid()) = id);
CREATE POLICY "Users create own profile" ON public.profiles
  FOR INSERT TO authenticated WITH CHECK ((SELECT auth.uid()) = id);
CREATE POLICY "Users edit own profile" ON public.profiles
  FOR UPDATE TO authenticated USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);
