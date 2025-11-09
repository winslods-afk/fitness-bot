-- ============================================
-- SQL ЗАПРОСЫ ДЛЯ БАЗЫ ДАННЫХ FITNESS BOT
-- ============================================

-- 1. ПОСМОТРЕТЬ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
SELECT 
    id,
    telegram_id,
    created_at
FROM users
ORDER BY created_at DESC;

-- 2. ПОСМОТРЕТЬ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ С КОЛИЧЕСТВОМ ПРОГРАММ
SELECT 
    u.id,
    u.telegram_id,
    u.created_at,
    COUNT(s.session_id) as programs_count
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
GROUP BY u.id, u.telegram_id, u.created_at
ORDER BY u.created_at DESC;

-- 3. ПОСМОТРЕТЬ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ С ПОЛНОЙ СТАТИСТИКОЙ
SELECT 
    u.id,
    u.telegram_id,
    u.created_at,
    COUNT(DISTINCT s.session_id) as programs_count,
    COUNT(DISTINCT sr.id) as workouts_count,
    COUNT(DISTINCT ps.id) as sets_count
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN session_runs sr ON u.id = sr.user_id
LEFT JOIN performed_sets ps ON sr.id = ps.session_run_id
GROUP BY u.id, u.telegram_id, u.created_at
ORDER BY u.created_at DESC;

-- 4. ПОСМОТРЕТЬ ВСЕ ПРОГРАММЫ
SELECT 
    s.session_id,
    s.name,
    u.telegram_id as user_telegram_id,
    s.created_at,
    COUNT(DISTINCT wd.id) as days_count
FROM sessions s
JOIN users u ON s.user_id = u.id
LEFT JOIN workout_days wd ON s.session_id = wd.session_id
GROUP BY s.session_id, s.name, u.telegram_id, s.created_at
ORDER BY s.created_at DESC;

-- 5. ПОСМОТРЕТЬ ПРОГРАММЫ КОНКРЕТНОГО ПОЛЬЗОВАТЕЛЯ (замените TELEGRAM_ID)
SELECT 
    s.session_id,
    s.name,
    s.created_at,
    COUNT(DISTINCT wd.id) as days_count
FROM sessions s
JOIN users u ON s.user_id = u.id
LEFT JOIN workout_days wd ON s.session_id = wd.session_id
WHERE u.telegram_id = 389624620  -- ЗАМЕНИТЕ НА НУЖНЫЙ TELEGRAM_ID
GROUP BY s.session_id, s.name, s.created_at
ORDER BY s.created_at DESC;

-- 6. ПОСМОТРЕТЬ ВСЕ ТРЕНИРОВКИ
SELECT 
    sr.id,
    sr.started_at,
    u.telegram_id as user_telegram_id,
    s.name as program_name,
    COUNT(DISTINCT ps.id) as sets_count
FROM session_runs sr
JOIN users u ON sr.user_id = u.id
LEFT JOIN sessions s ON sr.session_id = s.session_id
LEFT JOIN performed_sets ps ON sr.id = ps.session_run_id
GROUP BY sr.id, sr.started_at, u.telegram_id, s.name
ORDER BY sr.started_at DESC
LIMIT 50;

-- 7. ПОСМОТРЕТЬ ПОСЛЕДНИЕ ТРЕНИРОВКИ ПОЛЬЗОВАТЕЛЯ (замените TELEGRAM_ID)
SELECT 
    sr.id,
    sr.started_at,
    s.name as program_name,
    COUNT(DISTINCT ps.id) as sets_count
FROM session_runs sr
JOIN users u ON sr.user_id = u.id
LEFT JOIN sessions s ON sr.session_id = s.session_id
LEFT JOIN performed_sets ps ON sr.id = ps.session_run_id
WHERE u.telegram_id = 389624620  -- ЗАМЕНИТЕ НА НУЖНЫЙ TELEGRAM_ID
GROUP BY sr.id, sr.started_at, s.name
ORDER BY sr.started_at DESC
LIMIT 20;

-- 8. ПОСМОТРЕТЬ ВСЕ УПРАЖНЕНИЯ С ПОДХОДАМИ
SELECT 
    e.exercise_id,
    e.name,
    wd.name as day_name,
    s.name as program_name,
    COUNT(DISTINCT st.set_id) as sets_count,
    GROUP_CONCAT(st.reps, '-') as reps
FROM exercises e
JOIN workout_days wd ON e.workout_day_id = wd.id
JOIN sessions s ON wd.session_id = s.session_id
LEFT JOIN sets st ON e.exercise_id = st.exercise_id
GROUP BY e.exercise_id, e.name, wd.name, s.name
ORDER BY s.name, wd.day_index, e.order;

-- 9. ПОСМОТРЕТЬ ВЫПОЛНЕННЫЕ ПОДХОДЫ С ВЕСАМИ
SELECT 
    ps.id,
    ps.set_index,
    ps.weight,
    ps.timestamp,
    e.name as exercise_name,
    u.telegram_id as user_telegram_id,
    s.name as program_name
FROM performed_sets ps
JOIN exercises e ON ps.exercise_id = e.exercise_id
JOIN session_runs sr ON ps.session_run_id = sr.id
JOIN users u ON sr.user_id = u.id
LEFT JOIN sessions s ON sr.session_id = s.session_id
ORDER BY ps.timestamp DESC
LIMIT 100;

-- 10. СТАТИСТИКА ПО ВЕСАМ ДЛЯ КОНКРЕТНОГО УПРАЖНЕНИЯ
SELECT 
    ps.set_index,
    MIN(ps.weight) as min_weight,
    MAX(ps.weight) as max_weight,
    AVG(ps.weight) as avg_weight,
    COUNT(*) as attempts_count,
    MAX(ps.timestamp) as last_workout
FROM performed_sets ps
JOIN exercises e ON ps.exercise_id = e.exercise_id
WHERE e.name LIKE '%Гакк-присед%'  -- ЗАМЕНИТЕ НА НУЖНОЕ УПРАЖНЕНИЕ
GROUP BY ps.set_index
ORDER BY ps.set_index;

-- 11. ОБЩАЯ СТАТИСТИКА
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM sessions) as total_programs,
    (SELECT COUNT(*) FROM session_runs) as total_workouts,
    (SELECT COUNT(*) FROM performed_sets) as total_sets,
    (SELECT COUNT(DISTINCT exercise_id) FROM exercises) as total_exercises;

-- 12. ПОЛЬЗОВАТЕЛИ БЕЗ ПРОГРАММ
SELECT 
    u.id,
    u.telegram_id,
    u.created_at
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
WHERE s.session_id IS NULL;

-- 13. ПОЛЬЗОВАТЕЛИ БЕЗ ТРЕНИРОВОК
SELECT 
    u.id,
    u.telegram_id,
    u.created_at,
    COUNT(s.session_id) as programs_count
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN session_runs sr ON u.id = sr.user_id
WHERE sr.id IS NULL
GROUP BY u.id, u.telegram_id, u.created_at;

-- 14. САМЫЕ АКТИВНЫЕ ПОЛЬЗОВАТЕЛИ (по количеству тренировок)
SELECT 
    u.telegram_id,
    COUNT(DISTINCT sr.id) as workouts_count,
    COUNT(DISTINCT s.session_id) as programs_count,
    COUNT(DISTINCT ps.id) as sets_count,
    MAX(sr.started_at) as last_workout
FROM users u
LEFT JOIN session_runs sr ON u.id = sr.user_id
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN performed_sets ps ON sr.id = ps.session_run_id
GROUP BY u.telegram_id
HAVING workouts_count > 0
ORDER BY workouts_count DESC;

-- 15. ПОСЛЕДНИЕ РЕГИСТРАЦИИ
SELECT 
    telegram_id,
    created_at,
    (SELECT COUNT(*) FROM sessions WHERE user_id = users.id) as programs_count
FROM users
ORDER BY created_at DESC
LIMIT 20;

