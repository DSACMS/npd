--
-- Add field required to flagstate
--
ALTER TABLE "flags_flagstate"
ADD COLUMN "required" boolean DEFAULT false NOT NULL;

ALTER TABLE "flags_flagstate"
ALTER COLUMN "required"
DROP DEFAULT;