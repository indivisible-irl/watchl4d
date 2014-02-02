BEGIN;

ALTER TABLE "pairing" ADD COLUMN "create_date" timestamp with time zone NOT NULL;

ALTER TABLE "post" DROP COLUMN "image";

ALTER TABLE "post" ADD COLUMN "file" varchar(200);

ALTER TABLE "post" ADD COLUMN "file_name" varchar(200);

ALTER TABLE "map" DROP COLUMN "image";

ALTER TABLE "map" DROP COLUMN "download";

COMMIT;