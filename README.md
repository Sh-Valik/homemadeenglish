# HomeMade English 🌌

Пошаговое изучение английского языка — Streamlit web-приложение.

## Запуск локально

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Приложение будет доступно на `http://localhost:8501`

## Деплой на Streamlit Community Cloud

### 1. Сохранение прогресса в БД
На Streamlit Cloud локальные файлы сбрасываются при перезапуске сервера (app reboot). Чтобы профили пользователей и их прогресс сохранялись **навсегда**, вам нужно использовать внешнюю базу данных (например, [Supabase](https://supabase.com/) или Neon). 
Это бесплатно и очень просто:
1. Создайте PostgreSQL БД.
2. Скопируйте строку подключения (Connection URL).
3. В настройках вашего приложения на Streamlit (App Settings -> Secrets) добавьте:
   ```toml
   DB_URL = "postgresql://user:pass@host:port/dbname"
   ```
Если `DB_URL` не указан, приложение автоматически будет использовать локальный файл `learner.db`.

### 2. Деплой
1. Зайдите на [share.streamlit.io](https://share.streamlit.io)
2. Авторизуйтесь через GitHub
3. Нажмите **"New app"**
4. Выберите:
   - **Repository:** ваш репозиторий
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
5. В поле **"App URL"** введите: `homemadeenglish`
6. Добавьте URL базы данных в **Advanced settings -> Secrets** (см. выше).
7. Нажмите **"Deploy!"**

## Готово!
Приложение будет доступно по адресу:
`https://homemadeenglish.streamlit.app`
