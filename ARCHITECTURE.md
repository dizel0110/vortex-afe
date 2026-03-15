# 🪁 V-AFE: Архитектура интеграции репозиториев

## 📊 Проблема решена

**До:**
- ❌ Lite-версия без истории диалога
- ❌ Поиск только по keywords
- ❌ Нет связи между `vortex-afe` и `dizel0110.github.io`
- ❌ Ручное копирование файлов

**После:**
- ✅ История диалога с контекстным поиском
- ✅ Автоматическая синхронизация через `scripts/sync_widget.py`
- ✅ Единый источник истины — `v-afe_core.json`
- ✅ 34 концепта с физикой и механикой

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    V-AFE ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────┐         ┌────────────────────────┐ │
│  │  vortex-afe       │         │  dizel0110.github.io   │ │
│  │  (Source of Truth)│  SYNC   │  (GitHub Pages)        │ │
│  │                   │────────►│                        │ │
│  │  data/            │         │  src/components/       │ │
│  │    v-afe_core.json│         │    VafeChatWidget.tsx  │ │
│  │                   │         │                        │ │
│  │  scripts/         │         │  Public:               │ │
│  │    sync_widget.py │         │    dizel0110.github.io │ │
│  └───────────────────┘         └────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow синхронизации

### 1. Обновление ядра знаний

```bash
# 1. Измени data/v-afe_core.json
# Добавь новый концепт:
{
  "id": 35,
  "tag": "NewCategory",
  "concept": "Новый концепт",
  "physics": "Физическое описание",
  "mechanics": "Механика выполнения"
}

# 2. Запусти синхронизацию
python scripts/sync_widget.py

# 3. Закоммить изменения
git add .
git commit -m "Add new concept: Новый концепт"
git push
```

### 2. Деплой на GitHub Pages

```bash
# vortex-afe
cd d:\ai\vortex-afe
git push

# dizel0110.github.io
cd d:\ai\dizel0110.github.io
git add .
git commit -m "Sync V-AFE knowledge base"
git push
```

---

## 🎯 Улучшения чата (v2.0)

### История диалога

```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Concept[];
  timestamp: number;  // ← Новое!
}
```

**Преимущества:**
- Контекстный поиск учитывает последние 3 сообщения
- Связь между темами ("это связано с вашим предыдущим вопросом")
- Временные метки для каждого сообщения

### Контекстный поиск

```typescript
const searchWithContext = (
  query: string, 
  history: Message[],  // ← Используется для контекста!
  topK: number = 3
): Concept[] => {
  // Извлекаем ключевые слова из запроса + истории
  const contextWords = [
    ...extractKeywords(query),
    ...history.slice(-3).flatMap(m => extractKeywords(m.content))
  ];
  
  // Скоринг с учётом контекста
  // ...
}
```

**Пример:**
```
User: "Как правильно стартовать?"
Assistant: [нашёл концепты про старт]

User: "А как потом ехать вверх?"
Assistant: [понимает контекст "апвинд" из предыдущего вопроса]
```

### Улучшенный UI

- **Highlighting** — ключевые слова подсвечиваются
- **Timestamps** — время каждого сообщения
- **Clear History** — кнопка очистки истории 🗑️
- **Markdown-like** — поддержка `**bold**`, переносов строк

---

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Концептов | 34 |
| Категорий | 12 |
| Доменов | 5 (PHYSICS, MECHANICS, etc.) |
| Среднее время ответа | <1 сек |
| Размер базы | ~15KB |

---

## 🚀 Roadmap

### Q2 2026 — Backend Integration

```
┌───────────────────┐         ┌──────────────────┐
│  GitHub Pages     │  HTTPS  │  Hugging Face    │
│  (Frontend)       │────────►│  Spaces (API)    │
│                   │         │                  │
│  VafeChatWidget   │         │  FastAPI +       │
│                   │         │  RAPTOR RAG      │
└───────────────────┘         └──────────────────┘
```

**Преимущества:**
- ✅ LLM-генерация ответов (Google Gemini)
- ✅ Семантический поиск (sentence-transformers)
- ✅ История сессий в базе данных
- ✅ Аналитика использования

### Q3 2026 — Session Parser

- Автоматическое извлечение инсайтов из YAML-сессий
- Обновление ядра через RAG
- Валидация физики

### Q4 2026 — Mobile App

- React Native версия
- Офлайн режим
- Голосовой ввод

---

## 🛠️ Команды

### Локальная разработка

```bash
# 1. Запуск из vortex-afe
cd d:\ai\vortex-afe
python scripts/dev.py

# 2. Или вручную
cd d:\ai\dizel0110.github.io
npm run dev
```

### Синхронизация

```bash
# Обновить виджет из core.json
python scripts/sync_widget.py
```

### Деплой

```bash
# vortex-afe
git push

# dizel0110.github.io
git add .
git commit -m "Sync V-AFE widget"
git push
```

---

## 📞 Контакты

**Дмитрий Зеленин (@dizel0110)**
- GitHub: https://github.com/dizel0110
- Портфолио: https://dizel0110.github.io/
- Email: dizel0110@gmail.com

---

**V-AFE v2.0** — От тактильного опыта к цифровой базе знаний! 🪁
