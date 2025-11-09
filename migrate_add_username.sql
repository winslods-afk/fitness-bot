-- Миграция: Добавление поля username в таблицу users
-- Выполните этот SQL запрос в PostgreSQL через DBeaver или Railway CLI

-- Добавляем колонку username (может быть NULL, так как не у всех пользователей есть username)
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR;

-- Создаем индекс для быстрого поиска по username
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

-- Комментарий к колонке
COMMENT ON COLUMN users.username IS 'Telegram username пользователя (может быть NULL)';

-- Проверка: посмотреть структуру таблицы
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'users' AND table_schema = 'public';

