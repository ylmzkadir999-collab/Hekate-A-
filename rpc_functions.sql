-- Add this RPC function to Supabase SQL Editor
-- Called from backend to safely increment daily message count

create or replace function increment_message_count(uid uuid)
returns void language plpgsql security definer as $$
begin
  -- Reset if new day
  update profiles
  set
    daily_message_count = case
      when daily_message_reset_at < current_date then 1
      else daily_message_count + 1
    end,
    daily_message_reset_at = current_date,
    total_readings = total_readings + 1
  where id = uid;
end;
$$;
