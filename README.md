# VORTEX: APPARENT FLOW ENGINE (V-AFE) v2.0

An engineering and ML-inspired approach to systematizing kiteboarding mechanics.

## Core Equation
$$ \vec{W_{app}} = \vec{W_{true}} + \vec{W_{board}} $$

## 🚀 Что нового в v2.0

- **RAPTOR-inspired RAG** — древовидная организация знаний с уровнями абстракции
- **FastAPI Backend** — REST API для интеграции с веб-приложениями
- **Chat Widget** — готовый чат-бот для GitHub Pages
- **Семантический поиск** — поиск концептов по смыслу, а не по ключевым словам

## 📁 Архитектура

```
vortex-afe/
├── data/
│   ├── v-afe_core.json        # Ядро знаний (34 концепта)
│   └── v-afe_core.md          # Markdown версия
├── scripts/
│   ├── raptor_rag.py          # RAPTOR RAG движок
│   ├── api.py                 # FastAPI backend
│   └── v_afe_sync.py          # Sync утилита
├── web/
│   └── chat.html              # Chat widget для GitHub Pages
├── logs/
│   ├── sessions/              # YAML сессии
│   └── template.yaml          # Шаблон сессии
├── .github/workflows/
│   └── deploy.yml             # CI/CD пайплайн
├── requirements.txt           # Python зависимости
├── INTEGRATION.md             # Инструкция по интеграции
└── README.md                  # Этот файл
```

## 🔧 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск API

```bash
cd scripts
python api.py
```

API доступен по адресу: http://localhost:8000

### 3. Тестирование RAG

```bash
python scripts/test_rag.py
```

## 🌐 Интеграция с GitHub Pages

Чат-виджет перенесён в `dizel0110.github.io`.

## 📊 API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Информация об API |
| GET | `/api/health` | Проверка здоровья |
| POST | `/api/chat` | Запрос к AI-инструктору |
| GET | `/api/knowledge-base` | Получить все концепты |
| GET | `/api/knowledge-base/{id}` | Получить концепт по ID |
| GET | `/api/tags` | Получить все теги |
| POST | `/api/index/rebuild` | Перестроить индекс |

### Пример запроса к чату:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Что такое вымпельный ветер?",
    "top_k": 3,
    "use_llm": false
  }'
```

## 🧠 RAPTOR RAG

### Уровни абстракции:

```
L3: Домены (PHYSICS, MECHANICS, MANEUVERS, FEEDBACK, PHILOSOPHY)
     │
L2: Категории (Aerodynamics, Kinematics, Control, etc.)
     │
L1: Концепты (ID 1-34 из v-afe_core.json)
```

### Стратегии поиска:

- **Collapsed Tree** — поиск по всем узлам одновременно (рекомендуется)
- **Tree Traversal** — послойный обход сверху вниз

## 📝 Использование сессий

1. Создайте YAML-файл в `logs/sessions/` по шаблону
2. Используйте RAG для извлечения инсайтов
3. Обновите `v-afe_core.json` новыми концептами

## 🛠 Технологии

- **Python 3.10+**
- **FastAPI** — REST API
- **Sentence Transformers** — эмбеддинги
- **scikit-learn** — кластеризация
- **RAPTOR** — рекурсивная абстрактивная обработка

## 📈 Roadmap

- [ ] Подключение Google Gemini API для генерации ответов
- [ ] Session parser для автоматического извлечения инсайтов
- [ ] Визуализация дерева знаний
- [ ] Экспорт в различные форматы (PDF, Notion, Obsidian)
- [ ] Мобильное приложение

## 👨‍💻 Автор

**Дмитрий Зеленин (@dizel0110)**
- GitHub: https://github.com/dizel0110
- Портфолио: https://dizel0110.github.io/

## 📄 Лицензия

MIT License

---

**V-AFE** — превращаем тактильный опыт в дискретную базу знаний через физику и инженерию.
