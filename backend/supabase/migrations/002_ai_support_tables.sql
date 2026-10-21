CREATE SCHEMA IF NOT EXISTS querypilot;

CREATE TABLE querypilot.schema_documents (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_type text NOT NULL CHECK (document_type IN ('table','column','relationship','metric','policy')),
    object_name   text NOT NULL,
    content       text NOT NULL,
    updated_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (document_type, object_name)
);

CREATE TABLE querypilot.query_examples (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question    text NOT NULL,
    language    text NOT NULL CHECK (language IN ('english','roman_urdu','mixed')),
    sql         text NOT NULL,
    explanation text NOT NULL,
    approved    boolean NOT NULL DEFAULT false,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE querypilot.query_feedback (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id    text NOT NULL,
    rating        smallint NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_text text CHECK (char_length(feedback_text) <= 500),
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE querypilot.query_audit (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id    text NOT NULL,
    user_id       text,
    status        text NOT NULL,
    duration_ms   integer,
    model_name    text,
    input_tokens  integer,
    output_tokens integer,
    created_at    timestamptz NOT NULL DEFAULT now()
);
-- Privacy rule: yahan raw prompts, result rows ya emails store nahi hote.