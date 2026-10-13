# RateNest

### Клонирование репозитория
```
git clone https://github.com/Kirichenkodv/RateNest.git
cd RateNest
```
### Установка `uv`
**macOS и Linux:**

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows (PowerShell):
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
### Установка зависимостей
```
uv sync
```
### Настройка переменных окружения
```
cp .env.example .env
```
переменные из .env заполнить своими данными

### Запуск приложения
```
uv run --env-file .env python manage.py runserver
```
### Запуск тестов
```
uv run pytest
```


