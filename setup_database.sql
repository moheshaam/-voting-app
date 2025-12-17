-- Create votes table in Supabase
CREATE TABLE IF NOT EXISTS votes (
    id BIGSERIAL PRIMARY KEY,
    voter TEXT NOT NULL,
    question INTEGER NOT NULL,
    choice TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries by voter
CREATE INDEX IF NOT EXISTS idx_votes_voter ON votes(voter);

-- Create index for faster queries by question
CREATE INDEX IF NOT EXISTS idx_votes_question ON votes(question);

-- Enable Row Level Security (RLS)
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (since we're using anon key)
CREATE POLICY "Enable all access for anon users" ON votes
    FOR ALL
    USING (true)
    WITH CHECK (true);
