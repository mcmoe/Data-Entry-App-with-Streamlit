CREATE DATABASE phone_db;

\connect "phone_db";

DROP TABLE IF EXISTS "phone_sales";
DROP SEQUENCE IF EXISTS phone_sales_id_seq;
CREATE SEQUENCE phone_sales_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 32767 CACHE 1;

CREATE TABLE "public"."phone_sales" (
    "id" smallint DEFAULT nextval('phone_sales_id_seq') NOT NULL,
    "phone_brand" text NOT NULL,
    "phone_model" text NOT NULL,
    "purchase_date" date NOT NULL,
    "sold_date" date NOT NULL,
    "sold_price" real NOT NULL,
    "cost_price" real NOT NULL,
    "profit" real,
    CONSTRAINT "phone_sales_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

INSERT INTO "phone_sales" ("phone_brand", "phone_model", "purchase_date", "sold_date", "sold_price", "cost_price", "id", "profit") VALUES
('Apple',	'iPhone 7',	'2024-09-11',	'2024-09-11',	700,	350,	2,	350);
