ALTER TABLE runs
  ADD COLUMN support_count INTEGER,
  ADD COLUMN reject_count INTEGER,
  ADD COLUMN conditional_count INTEGER,
  ADD COLUMN synthesis_summary TEXT,
  ADD COLUMN synthesis_main_barriers TEXT[],
  ADD COLUMN synthesis_winning_conditions TEXT,
  ADD COLUMN synthesis_best_target_segment TEXT,
  ADD COLUMN synthesis_strategic_recommendation TEXT;
