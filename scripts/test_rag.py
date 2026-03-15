#!/usr/bin/env python3
"""
V-AFE RAG Demo Script
Тестирование RAPTOR RAG системы
"""

import json
import sys
from pathlib import Path

# Добавляем parent directory в path
sys.path.insert(0, str(Path(__file__).parent))

from raptor_rag import RaptorIndex, VAFERAG


def load_core_data():
    """Загрузка ядра знаний"""
    core_path = Path(__file__).parent.parent / "data" / "v-afe_core.json"
    with open(core_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_index_build():
    """Тест построения индекса"""
    print("=" * 60)
    print("ТЕСТ 1: Построение RAPTOR индекса")
    print("=" * 60)
    
    core_data = load_core_data()
    index = RaptorIndex(model_name='all-MiniLM-L6-v2')
    index.build_from_core(core_data)
    
    print(f"\n✓ Ядро загружено: {len(core_data.get('knowledge_base', []))} концептов")
    print(f"\n📊 Структура дерева:")
    print(f"   L1 (Концепты):    {len(index.tree_levels[1])} узлов")
    print(f"   L2 (Категории):   {len(index.tree_levels[2])} узлов")
    print(f"   L3 (Домены):      {len(index.tree_levels[3])} узлов")
    print(f"   Всего узлов:      {len(index.nodes)}")
    
    return index


def test_retrieval(index):
    """Тест поиска"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Семантический поиск")
    print("=" * 60)
    
    test_queries = [
        "Как правильно стартовать?",
        "Что такое вымпельный ветер?",
        "Как ехать против ветра (апвинд)?",
        "Поза семёрки — как правильно?",
        "Как использовать чоп для прыжка?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Запрос: {query}")
        print("-" * 50)
        
        results = index.retrieve(query, top_k=3, strategy='collapsed_tree')
        
        for i, result in enumerate(results, 1):
            concept = result['metadata'].get('concept_name', 'Unknown')
            tag = result['metadata'].get('tag', '')
            similarity = result['similarity']
            
            print(f"   {i}. [{tag}] {concept}")
            print(f"      Сходство: {similarity:.3f}")
    
    print("\n✓ Тест поиска завершён")


def test_rag_engine():
    """Тест полного RAG движка"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: V-AFE RAG Engine (с генерацией ответов)")
    print("=" * 60)
    
    core_data = load_core_data()
    index = RaptorIndex(model_name='all-MiniLM-L6-v2')
    index.build_from_core(core_data)
    
    # Создаём заглушку LLM
    class DummyLLM:
        def generate(self, prompt: str) -> str:
            return "🤖 [LLM ответ] Для полной генерации подключите Google Gemini API"
    
    rag = VAFERAG(index=index, llm_client=DummyLLM())
    
    test_questions = [
        "Как мне быстро выйти на глиссирование?",
        "Почему кайт падает в одну сторону?",
        "Когда нужно переступать ногами?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Вопрос: {question}")
        print("-" * 50)
        
        result = rag.query(question, top_k=2, use_llm=False)
        
        print(f"\n📋 Ответ:\n{result['answer']}")
        
        if result['sources']:
            print(f"\n📚 Источники:")
            for source in result['sources']:
                print(f"   • {source.get('concept', source.get('id'))} [{source.get('tag', '')}]")
    
    print("\n✓ Тест RAG движка завершён")


def test_tree_traversal():
    """Тест послойного обхода дерева"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Tree Traversal (послойный обход)")
    print("=" * 60)
    
    core_data = load_core_data()
    index = RaptorIndex(model_name='all-MiniLM-L6-v2')
    index.build_from_core(core_data)
    
    query = "техника разворота против ветра"
    print(f"\n🔍 Запрос: {query}")
    
    # Collapsed Tree
    print("\n📊 Collapsed Tree Strategy:")
    results_collapsed = index.retrieve(query, top_k=3, strategy='collapsed_tree')
    for r in results_collapsed:
        print(f"   • {r['metadata'].get('concept_name')} ({r['metadata'].get('tag')})")
    
    # Tree Traversal
    print("\n📊 Tree Traversal Strategy:")
    results_tree = index.retrieve(query, top_k=3, strategy='tree_traversal')
    for r in results_tree:
        print(f"   • {r['metadata'].get('concept_name')} ({r['metadata'].get('tag')})")
    
    print("\n✓ Тест обхода дерева завершён")


def export_index_structure():
    """Экспорт структуры индекса для отладки"""
    print("\n" + "=" * 60)
    print("ЭКСПОРТ: Структура индекса")
    print("=" * 60)
    
    core_data = load_core_data()
    index = RaptorIndex(model_name='all-MiniLM-L6-v2')
    index.build_from_core(core_data)
    
    # L3: Домены
    print("\n🏛️ L3 — Домены:")
    for nid in index.root_ids:
        node = index.nodes[nid]
        print(f"   {node.metadata.get('domain')}: {len(node.children)} категорий")
    
    # L2: Категории
    print("\n📁 L2 — Категории:")
    for nid in index.tree_levels[2]:
        node = index.nodes[nid]
        print(f"   {node.metadata.get('tag')}: {node.metadata.get('concept_count')} концептов")
    
    # L1: Концепты по тегам
    print("\n📌 L1 — Концепты (по тегам):")
    tag_groups = {}
    for nid in index.tree_levels[1]:
        node = index.nodes[nid]
        tag = node.metadata.get('tag', 'Unknown')
        if tag not in tag_groups:
            tag_groups[tag] = []
        tag_groups[tag].append(node.metadata.get('concept_name', 'Unknown'))
    
    for tag, concepts in sorted(tag_groups.items()):
        print(f"\n   [{tag}]")
        for c in concepts:
            print(f"      • {c}")
    
    print("\n✓ Экспорт завершён")


def main():
    """Запуск всех тестов"""
    print("\n" + "🪁 " * 20)
    print("V-AFE RAPTOR RAG — Тестирование системы")
    print("🪁 " * 20)
    
    try:
        # Тест 1: Построение индекса
        index = test_index_build()
        
        # Тест 2: Поиск
        test_retrieval(index)
        
        # Тест 3: RAG движок
        test_rag_engine()
        
        # Тест 4: Обход дерева
        test_tree_traversal()
        
        # Экспорт структуры
        export_index_structure()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ")
        print("=" * 60)
        print("\n📝 Следующие шаги:")
        print("   1. Запустите API: python scripts/api.py")
        print("   2. Откройте web/chat.html в браузере")
        print("   3. Интегрируйте widget на GitHub Pages")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
