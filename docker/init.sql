-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS email_rules;

-- Connect to the database
\c email_rules;

-- Create enum types
CREATE TYPE match_type AS ENUM ('all', 'any');
CREATE TYPE field_type AS ENUM ('from', 'subject', 'message', 'received_date');
CREATE TYPE predicate_type AS ENUM ('contains', 'does_not_contain', 'equals', 'does_not_equal', 'less_than', 'greater_than');
CREATE TYPE action_type AS ENUM ('mark_as_read', 'mark_as_unread', 'move_message');

-- Create rules table
CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    match_type match_type NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create conditions table
CREATE TABLE IF NOT EXISTS conditions (
    id UUID PRIMARY KEY,
    rule_id UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    field field_type NOT NULL,
    predicate predicate_type NOT NULL,
    value TEXT NOT NULL,
    unit VARCHAR(50)
);

-- Create actions table
CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY,
    rule_id UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    type action_type NOT NULL,
    target VARCHAR(255)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conditions_rule_id ON conditions(rule_id);
CREATE INDEX IF NOT EXISTS idx_actions_rule_id ON actions(rule_id); 