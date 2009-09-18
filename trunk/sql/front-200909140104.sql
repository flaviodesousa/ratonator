BEGIN;
CREATE TABLE "front_language" (
    "id" serial NOT NULL PRIMARY KEY,
    "code" varchar(2) NOT NULL UNIQUE,
    "name" varchar(64) NOT NULL UNIQUE,
    "nativeName" varchar(64) NOT NULL UNIQUE
)
;
CREATE TABLE "front_rateablestuff" (
    "id" serial NOT NULL PRIMARY KEY,
    "createdAt" timestamp with time zone NOT NULL,
    "lastTouchedAt" timestamp with time zone NOT NULL,
    "createdBy_id" integer,
    "uuid" varchar(36) NOT NULL UNIQUE
)
;
CREATE TABLE "front_rate" (
    "rateablestuff_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_rateablestuff" ("id") DEFERRABLE INITIALLY DEFERRED,
    "theRate" smallint NOT NULL,
    "comments" text,
    "superseder_id" integer UNIQUE,
    "subject_id" integer NOT NULL REFERENCES "front_rateablestuff" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
ALTER TABLE "front_rate" ADD CONSTRAINT "superseder_id_refs_rateablestuff_ptr_id_322a0475" FOREIGN KEY ("superseder_id") REFERENCES "front_rate" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "front_nameablerateablestuff" (
    "rateablestuff_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_rateablestuff" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(255) NOT NULL,
    "nameSlugged" varchar(255) NOT NULL,
    "language" varchar(2) NOT NULL,
    "disambiguator_id" integer,
    UNIQUE ("language", "name"),
    UNIQUE ("language", "nameSlugged")
)
;
CREATE TABLE "front_aspect" (
    "nameablerateablestuff_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_nameablerateablestuff" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "front_aspectrate" (
    "rate_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_rate" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED,
    "aspect_id" integer NOT NULL REFERENCES "front_aspect" ("nameablerateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED,
    "baseRate_id" integer NOT NULL REFERENCES "front_rate" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "front_classifiablerateablestuff" (
    "nameablerateablestuff_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_nameablerateablestuff" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "front_classification" (
    "rateablestuff_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_rateablestuff" ("id") DEFERRABLE INITIALLY DEFERRED,
    "subject_id" integer NOT NULL REFERENCES "front_classifiablerateablestuff" ("nameablerateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED,
    "category_id" integer NOT NULL REFERENCES "front_classifiablerateablestuff" ("nameablerateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("subject_id", "category_id")
)
;
CREATE TABLE "front_definition" (
    "rateablestuff_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_rateablestuff" ("id") DEFERRABLE INITIALLY DEFERRED,
    "theDefinition" text NOT NULL,
    "subject_id" integer NOT NULL REFERENCES "front_classifiablerateablestuff" ("nameablerateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "front_disambiguator" (
    "id" serial NOT NULL PRIMARY KEY,
    "commonTerm" varchar(255) NOT NULL,
    "language" varchar(2) NOT NULL,
    UNIQUE ("commonTerm", "language")
)
;
ALTER TABLE "front_nameablerateablestuff" ADD CONSTRAINT "disambiguator_id_refs_id_5e0fdb15" FOREIGN KEY ("disambiguator_id") REFERENCES "front_disambiguator" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "front_kill" (
    "id" serial NOT NULL PRIMARY KEY,
    "killedAt" timestamp with time zone NOT NULL,
    "killer_id" integer NOT NULL,
    "killed_id" integer NOT NULL
)
;
CREATE TABLE "front_rateableuser" (
    "rateablestuff_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "front_rateablestuff" ("id") DEFERRABLE INITIALLY DEFERRED,
    "defaultLanguage" varchar(2) NOT NULL,
    "validatedAt" timestamp with time zone,
    "lastLoggedOnAt" timestamp with time zone,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
ALTER TABLE "front_rateablestuff" ADD CONSTRAINT "createdBy_id_refs_rateablestuff_ptr_id_48dbd2d3" FOREIGN KEY ("createdBy_id") REFERENCES "front_rateableuser" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "front_kill" ADD CONSTRAINT "killer_id_refs_rateablestuff_ptr_id_22691eb6" FOREIGN KEY ("killer_id") REFERENCES "front_rateableuser" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "front_kill" ADD CONSTRAINT "killed_id_refs_rateablestuff_ptr_id_22691eb6" FOREIGN KEY ("killed_id") REFERENCES "front_rateableuser" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "front_uservalidation" (
    "id" serial NOT NULL PRIMARY KEY,
    "uuid" varchar(36) NOT NULL UNIQUE,
    "requestedAt" timestamp with time zone NOT NULL,
    "expiresAt" timestamp with time zone NOT NULL,
    "validatedAt" timestamp with time zone,
    "user_id" integer NOT NULL REFERENCES "front_rateableuser" ("rateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "front_aspect_subjects" (
    "id" serial NOT NULL PRIMARY KEY,
    "aspect_id" integer NOT NULL REFERENCES "front_aspect" ("nameablerateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED,
    "classifiablerateablestuff_id" integer NOT NULL REFERENCES "front_classifiablerateablestuff" ("nameablerateablestuff_ptr_id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("aspect_id", "classifiablerateablestuff_id")
)
;
CREATE INDEX "front_rateablestuff_createdBy_id" ON "front_rateablestuff" ("createdBy_id");
CREATE INDEX "front_rate_subject_id" ON "front_rate" ("subject_id");
CREATE INDEX "front_nameablerateablestuff_nameSlugged" ON "front_nameablerateablestuff" ("nameSlugged");
CREATE INDEX "front_nameablerateablestuff_disambiguator_id" ON "front_nameablerateablestuff" ("disambiguator_id");
CREATE INDEX "front_aspectrate_aspect_id" ON "front_aspectrate" ("aspect_id");
CREATE INDEX "front_aspectrate_baseRate_id" ON "front_aspectrate" ("baseRate_id");
CREATE INDEX "front_classification_subject_id" ON "front_classification" ("subject_id");
CREATE INDEX "front_classification_category_id" ON "front_classification" ("category_id");
CREATE INDEX "front_definition_subject_id" ON "front_definition" ("subject_id");
CREATE INDEX "front_kill_killer_id" ON "front_kill" ("killer_id");
CREATE INDEX "front_kill_killed_id" ON "front_kill" ("killed_id");
CREATE INDEX "front_uservalidation_user_id" ON "front_uservalidation" ("user_id");
COMMIT;
