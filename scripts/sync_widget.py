#!/usr/bin/env python3
"""
V-AFE Widget Sync
Синхронизирует v-afe_core.json с VafeChatWidget.tsx
"""

import json
from pathlib import Path
import shutil
from datetime import datetime

# Пути
VORTEX_AFE_DIR = Path(__file__).parent.parent
WEBSITE_DIR = Path("d:/ai/dizel0110.github.io")

CORE_JSON = VORTEX_AFE_DIR / "data/v-afe_core.json"
WIDGET_TEMPLATE = VORTEX_AFE_DIR / "web/VafeChatWidget.tsx"
WIDGET_SITE = WEBSITE_DIR / "src/components/VafeChatWidget.tsx"


def load_core():
    """Загрузка ядра знаний"""
    with open(CORE_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('knowledge_base', [])


def generate_knowledge_base_js(concepts: list) -> str:
    """Генерация JavaScript массива из JSON"""
    js_array = "const KNOWLEDGE_BASE = [\n"
    
    for c in concepts:
        # Экранируем кавычки
        concept = c['concept'].replace('"', '\\"')
        physics = c['physics'].replace('"', '\\"')
        mechanics = c['mechanics'].replace('"', '\\"')
        tag = c['tag'].replace('"', '\\"')
        
        js_array += f'  {{id:{c["id"]},tag:"{tag}",concept:"{concept}",physics:"{physics}",mechanics:"{mechanics}"}},\n'
    
    js_array += "];\n"
    return js_array


def sync_widget():
    """Синхронизация виджета"""
    print("🪁 V-AFE Widget Sync\n")
    
    # Загрузка ядра
    print(f"📖 Чтение {CORE_JSON}...")
    concepts = load_core()
    print(f"  ✓ Загружено {len(concepts)} концептов")
    
    # Генерация JS
    print("\n📝 Генерация KNOWLEDGE_BASE...")
    kb_js = generate_knowledge_base_js(concepts)
    
    # Чтение шаблона
    if WIDGET_TEMPLATE.exists():
        with open(WIDGET_TEMPLATE, 'r', encoding='utf-8') as f:
            widget_content = f.read()
    else:
        print(f"  ✗ Шаблон не найден: {WIDGET_TEMPLATE}")
        return False
    
    # Замена KNOWLEDGE_BASE
    start_marker = "// === БАЗА ЗНАНИЙ V-AFE (34 концепта) ==="
    end_marker = "const SUGGESTIONS ="
    
    if start_marker in widget_content and end_marker in widget_content:
        start_idx = widget_content.find(start_marker) + len(start_marker)
        end_idx = widget_content.find(end_marker)
        
        new_widget = (
            widget_content[:start_idx] + 
            "\n" + kb_js + 
            widget_content[end_idx:]
        )
    else:
        print("  ✗ Не найдены маркеры в шаблоне")
        return False
    
    # Сохранение в web/
    print(f"\n💾 Сохранение в {WIDGET_TEMPLATE}...")
    with open(WIDGET_TEMPLATE, 'w', encoding='utf-8') as f:
        f.write(new_widget)
    print("  ✓ Обновлено")
    
    # Копирование в сайт
    print(f"\n📦 Копирование в {WIDGET_SITE}...")
    shutil.copy2(WIDGET_TEMPLATE, WIDGET_SITE)
    print("  ✓ Синхронизировано")
    
    # Обновление suggestions из тегов
    print("\n🏷️  Обновление suggestions...")
    tags = set()
    for c in concepts[:10]:  # Берём первые 10 концептов
        tag = c['tag'].split('/')[0]
        if len(tag) < 15:  # Короткие теги
            tags.add(c['concept'].split(' ')[0])  # Первое слово
    
    suggestions = list(tags)[:6]
    print(f"  → Suggestions: {suggestions}")
    
    # Обновление suggestions в файле
    with open(WIDGET_TEMPLATE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_suggestions = 'const SUGGESTIONS = [\n    "Вымпельный ветер",\n    "Как стартовать?",\n    "Поза семёрки",\n    "Апвинд",\n    "Чоп",\n    "Кайт в зенит"\n  ];'
    new_suggestions = f'const SUGGESTIONS = [\n    "{suggestions[0] if len(suggestions) > 0 else "Вымпельный ветер"}",\n    "{suggestions[1] if len(suggestions) > 1 else "Старт"}",\n    "{suggestions[2] if len(suggestions) > 2 else "Поза 7"}",\n    "{suggestions[3] if len(suggestions) > 3 else "Апвинд"}",\n    "{suggestions[4] if len(suggestions) > 4 else "Чоп"}",\n    "{suggestions[5] if len(suggestions) > 5 else "Кайт"}"\n  ];'
    
    content = content.replace(old_suggestions, new_suggestions)
    
    with open(WIDGET_TEMPLATE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Копирование в сайт
    shutil.copy2(WIDGET_TEMPLATE, WIDGET_SITE)
    
    print("\n✅ Синхронизация завершена!")
    print(f"\n📊 Статистика:")
    print(f"   Концептов: {len(concepts)}")
    print(f"   Suggestions: {len(suggestions)}")
    print(f"\n📝 Следующие шаги:")
    print(f"   1. cd d:\\ai\\dizel0110.github.io")
    print(f"   2. git add .")
    print(f"   3. git commit -m 'Sync V-AFE knowledge base ({len(concepts)} concepts)'")
    print(f"   4. git push")
    
    return True


if __name__ == "__main__":
    sync_widget()
