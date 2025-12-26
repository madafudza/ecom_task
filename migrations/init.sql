CREATE TABLE IF NOT EXISTS grades (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    group_number VARCHAR(50) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    grade INTEGER NOT NULL CHECK (grade >= 2 AND grade <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_grades_full_name ON grades(full_name);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_grades_grade ON grades(grade);
