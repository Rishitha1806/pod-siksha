"""
Additive Database Migration for Pod-Siksha 2.0 — Universal AI Animated Learning Platform.
Adds video_projects, video_scenes, and user_learning_profiles to Neon PostgreSQL.
Safely preserves all existing 14 tables and 838+ rows.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(r"C:\Users\jvris\Downloads\pod-siksha\.env")
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not found")
    exit(1)

print("Connecting to Neon PostgreSQL...")
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

# 1. Video Projects (Lessons)
cur.execute("""
CREATE TABLE IF NOT EXISTS video_projects (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    topic TEXT NOT NULL,
    learner_profile TEXT DEFAULT 'teen', -- child, teen, university, professional, older_adult
    teaching_style TEXT DEFAULT 'visual_demonstration',
    animation_style TEXT DEFAULT 'educational_2d', -- cartoon, educational_2d, simulation, whiteboard, infographic
    language TEXT DEFAULT 'te',
    source_type TEXT DEFAULT 'topic', -- topic, question, document, paste, skill
    source_content TEXT,
    summary TEXT,
    total_scenes INTEGER DEFAULT 0,
    total_duration_sec REAL DEFAULT 0,
    video_url TEXT,
    status TEXT DEFAULT 'ready', -- drafting, generating, ready, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Video Scenes
cur.execute("""
CREATE TABLE IF NOT EXISTS video_scenes (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES video_projects(id) ON DELETE CASCADE,
    scene_index INTEGER NOT NULL,
    title TEXT NOT NULL,
    concept_tag TEXT NOT NULL,
    learning_objective TEXT,
    narration_text TEXT NOT NULL,
    display_text TEXT NOT NULL,
    animation_type TEXT NOT NULL, -- circulation, force_vectors, equation_transform, molecular_reaction, sorting_algorithm, cycle_loop, growth_curve, step_tutorial
    visual_spec JSONB NOT NULL DEFAULT '{}'::jsonb, -- declarative visual elements, particles, labels, colors
    duration_sec REAL DEFAULT 10.0,
    subtitles_spec JSONB DEFAULT '[]'::jsonb, -- array of {start_ms, end_ms, text}
    audio_url TEXT,
    checkpoint_question JSONB, -- interactive question after scene
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 3. User Learning Preferences
cur.execute("""
CREATE TABLE IF NOT EXISTS user_learning_preferences (
    user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_profile TEXT DEFAULT 'teen',
    default_language TEXT DEFAULT 'te',
    default_animation_style TEXT DEFAULT 'educational_2d',
    subtitles_enabled BOOLEAN DEFAULT TRUE,
    narration_speed REAL DEFAULT 1.0,
    font_size_scale REAL DEFAULT 1.0,
    high_contrast BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 4. Indexes for fast query performance & multi-tenant isolation
cur.execute("CREATE INDEX IF NOT EXISTS idx_video_projects_user ON video_projects(user_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_video_scenes_project ON video_scenes(project_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_video_scenes_index ON video_scenes(project_id, scene_index);")

# Verify all tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
""")
tables = [r[0] for r in cur.fetchall()]
print(f"Migration Complete! Total tables in Neon: {len(tables)}")
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t};")
    cnt = cur.fetchone()[0]
    print(f"  - {t}: {cnt} rows")

cur.close()
conn.close()
print("Additive migration executed successfully.")
