CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  user_id TEXT UNIQUE NOT NULL,
  name TEXT,
  email TEXT,
  education JSONB,
  projects JSONB,
  skills JSONB,
  experience JSONB,
  updated_at TIMESTAMP DEFAULT now()
);

INSERT INTO students (user_id, name, email, education, projects, skills, experience)
VALUES (
  'swaroop12',
  'swaroop',
  'swaroop@gmail.com',
  '[{"degree":"BTech CSE","year":2025,"institute":"XYZ"}]'::jsonb,
  '[{"name":"Seismic Classifier","desc":"P-wave vs noise using TCN","tech":["Python","TCN"]}]'::jsonb,
  '["Python","ML","TCN","PyTorch"]'::jsonb,
  '[]'::jsonb
) ON CONFLICT (user_id) DO NOTHING;
