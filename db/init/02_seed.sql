INSERT INTO users (full_name, email, role_name, city, is_active) VALUES
('Alice Rocha', 'alice@example.org', 'candidate', 'Belem', TRUE),
('Bruno Lima', 'bruno@example.org', 'candidate', 'Ananindeua', TRUE),
('Carla Mendes', 'carla@example.org', 'recruiter', 'Belem', TRUE),
('Diego Costa', 'diego@example.org', 'admin', 'Castanhal', TRUE),
('Elisa Santos', 'elisa@example.org', 'candidate', 'Maraba', FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO job_posts (title, department, location, salary_range, status) VALUES
('Back-end Developer', 'Engineering', 'Belem', '6000-8000', 'open'),
('Data Analyst', 'Analytics', 'Belem', '4500-6500', 'open'),
('Support Specialist', 'Operations', 'Ananindeua', '3000-4200', 'closed')
ON CONFLICT DO NOTHING;

INSERT INTO applications (user_id, job_post_id, application_status) VALUES
(1, 1, 'submitted'),
(2, 2, 'screening'),
(1, 2, 'interview'),
(5, 1, 'rejected')
ON CONFLICT DO NOTHING;

INSERT INTO admin_notes (related_user_id, note_text, note_tag, sensitivity_level) VALUES
(1, 'Candidate requested salary confidentiality.', 'internal', 'restricted'),
(2, 'Escalation requested by recruiter after profile review.', 'review', 'restricted'),
(4, 'Administrator account used for environment verification.', 'ops', 'secret')
ON CONFLICT DO NOTHING;
