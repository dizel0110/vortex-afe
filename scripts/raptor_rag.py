"""
V-AFE: RAPTOR-inspired RAG Engine
Рекурсивная абстрактивная обработка для древовидной организации знаний
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class AbstractionLevel(Enum):
    """Уровни абстракции в дереве знаний"""
    L0_RAW = 0        # Сырые данные (сессии)
    L1_CONCEPT = 1    # Концепты (ID 1-34)
    L2_CATEGORY = 2   # Категории (Physics, Mechanics, etc.)
    L3_DOMAIN = 3     # Домены (высокоуровневые темы)


@dataclass
class TreeNode:
    """Узел дерева знаний"""
    id: str
    level: AbstractionLevel
    content: str
    embedding: np.ndarray = field(repr=False)
    children: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def similarity(self, other: 'TreeNode') -> float:
        """Косинусное сходство с другим узлом"""
        return cosine_similarity(
            self.embedding.reshape(1, -1),
            other.embedding.reshape(1, -1)
        )[0][0]


class RaptorIndex:
    """
    RAPTOR-style индекс для V-AFE
    
    Построение дерева (снизу вверх):
    1. Сегментация → концепты из v-afe_core.json
    2. Встраивание → sentence-transformers эмбеддинги
    3. Кластеризация → KMeans на каждом уровне
    4. Суммаризация → создание абстракций кластеров
    5. Рекурсия → повторение для новых узлов
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.nodes: Dict[str, TreeNode] = {}
        self.tree_levels: Dict[int, List[str]] = {
            level: [] for level in range(4)
        }
        self.root_ids: List[str] = []
        
    def embed_text(self, text: str) -> np.ndarray:
        """Создание эмбеддинга текста"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def build_from_core(self, core_data: Dict[str, Any]) -> None:
        """
        Построение дерева знаний из v-afe_core.json
        
        Args:
            core_data: загруженный JSON из data/v-afe_core.json
        """
        knowledge_base = core_data.get('knowledge_base', [])
        
        # L1: Индексация концептов
        for concept in knowledge_base:
            node_id = f"l1_{concept['id']}"
            content = f"{concept['concept']}: {concept['physics']} {concept['mechanics']}"
            
            node = TreeNode(
                id=node_id,
                level=AbstractionLevel.L1_CONCEPT,
                content=content,
                embedding=self.embed_text(content),
                metadata={
                    'concept_id': concept['id'],
                    'tag': concept['tag'],
                    'concept_name': concept['concept'],
                    'physics': concept['physics'],
                    'mechanics': concept['mechanics']
                }
            )
            self.nodes[node_id] = node
            self.tree_levels[1].append(node_id)
        
        # L2: Кластеризация по тегам
        self._build_level_2(knowledge_base)
        
        # L3: Доменный уровень
        self._build_level_3()
        
    def _build_level_2(self, knowledge_base: List[Dict]) -> None:
        """
        L2: Группировка концептов по категориям (тегам)
        """
        tag_groups: Dict[str, List[str]] = {}
        
        for concept in knowledge_base:
            tag = concept['tag'].split('/')[0]  # Берём основной тег
            node_id = f"l1_{concept['id']}"
            
            if tag not in tag_groups:
                tag_groups[tag] = []
            tag_groups[tag].append(node_id)
        
        # Создаём узлы L2
        for tag, child_ids in tag_groups.items():
            node_id = f"l2_{tag}"
            
            # Агрегируем контент детей
            child_contents = [
                self.nodes[cid].metadata.get('concept', '') 
                for cid in child_ids
            ]
            content = f"Категория: {tag}. Концепты: {'; '.join(child_contents)}"
            
            node = TreeNode(
                id=node_id,
                level=AbstractionLevel.L2_CATEGORY,
                content=content,
                embedding=self.embed_text(content),
                children=child_ids,
                metadata={'tag': tag, 'concept_count': len(child_ids)}
            )
            self.nodes[node_id] = node
            self.tree_levels[2].append(node_id)
            
            # Обновляем детей
            for cid in child_ids:
                self.nodes[cid].metadata['parent_l2'] = node_id
    
    def _build_level_3(self) -> None:
        """
        L3: Доменный уровень (высокоуровневые абстракции)
        """
        domains = {
            'PHYSICS': ['Physics', 'Aerodynamics', 'Environment'],
            'MECHANICS': ['Kinematics', 'Control', 'Gear/Control'],
            'MANEUVERS': ['Manuever', 'Safety/Base'],
            'FEEDBACK': ['Feedback', 'Error', 'Error/Control'],
            'PHILOSOPHY': ['Philosophy/Zen', 'Architecture']
        }
        
        for domain, tags in domains.items():
            node_id = f"l3_{domain}"
            child_ids = [
                cid for cid in self.tree_levels[2]
                if self.nodes[cid].metadata.get('tag') in tags
            ]
            
            if not child_ids:
                continue
                
            content = f"Домен: {domain}. Категории: {', '.join(tags)}"
            
            node = TreeNode(
                id=node_id,
                level=AbstractionLevel.L3_DOMAIN,
                content=content,
                embedding=self.embed_text(content),
                children=child_ids,
                metadata={'domain': domain, 'category_count': len(tags)}
            )
            self.nodes[node_id] = node
            self.tree_levels[3].append(node_id)
            self.root_ids.append(node_id)
            
            # Обновляем детей
            for cid in child_ids:
                self.nodes[cid].metadata['parent_l3'] = node_id
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        strategy: str = 'collapsed_tree'
    ) -> List[Dict[str, Any]]:
        """
        Поиск релевантных узлов
        
        Args:
            query: поисковый запрос
            top_k: количество результатов
            strategy: 'tree_traversal' или 'collapsed_tree'
            
        Returns:
            Список релевантных узлов с метаданными
        """
        query_embedding = self.embed_text(query)
        query_node = TreeNode(
            id="query",
            level=AbstractionLevel.L0_RAW,
            content=query,
            embedding=query_embedding
        )
        
        if strategy == 'collapsed_tree':
            return self._collapsed_tree_search(query_node, top_k)
        else:
            return self._tree_traversal_search(query_node, top_k)
    
    def _collapsed_tree_search(
        self, 
        query_node: TreeNode, 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Collapsed Tree: поиск по всем узлам одновременно
        """
        all_nodes = [
            node for node in self.nodes.values()
            if node.level == AbstractionLevel.L1_CONCEPT
        ]
        
        similarities = [
            (node, query_node.similarity(node)) 
            for node in all_nodes
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                'id': node.id,
                'content': node.content,
                'metadata': node.metadata,
                'similarity': float(sim)
            }
            for node, sim in similarities[:top_k]
        ]
    
    def _tree_traversal_search(
        self, 
        query_node: TreeNode, 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Tree Traversal: послойный обход сверху вниз
        """
        results = []
        current_level_nodes = [
            self.nodes[nid] for nid in self.root_ids
        ]
        
        for level in [3, 2, 1]:
            if not current_level_nodes:
                break
                
            similarities = [
                (node, query_node.similarity(node))
                for node in current_level_nodes
            ]
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Выбираем лучшие узлы на уровне
            top_nodes = similarities[:max(1, top_k // (4 - level))]
            
            for node, sim in top_nodes:
                if node.level == AbstractionLevel.L1_CONCEPT:
                    results.append({
                        'id': node.id,
                        'content': node.content,
                        'metadata': node.metadata,
                        'similarity': float(sim)
                    })
                else:
                    # Спускаемся к детям
                    current_level_nodes = [
                        self.nodes[cid] 
                        for cid in node.children
                        if cid in self.nodes
                    ]
        
        return results[:top_k]
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация индекса"""
        return {
            'nodes': {
                nid: {
                    'id': node.id,
                    'level': node.level.value,
                    'content': node.content,
                    'children': node.children,
                    'metadata': node.metadata
                }
                for nid, node in self.nodes.items()
            },
            'tree_levels': self.tree_levels,
            'root_ids': self.root_ids
        }
    
    def save(self, path: str) -> None:
        """Сохранение индекса"""
        data = self.to_dict()
        # Эмбеддинги не сохраняем (пересоздаются при загрузке)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str, core_data: Dict[str, Any]) -> None:
        """
        Загрузка индекса
        
        Args:
            path: путь к сохранённому индексу
            core_data: данные ядра для восстановления эмбеддингов
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Восстанавливаем дерево
        self.tree_levels = {
            int(k): v for k, v in data['tree_levels'].items()
        }
        self.root_ids = data['root_ids']
        
        # Пересоздаём узлы с эмбеддингами
        self.build_from_core(core_data)


class VAFERAG:
    """
    Основной RAG-движок V-AFE
    
    Интегрирует RAPTOR-индекс с LLM для генерации ответов
    """
    
    def __init__(self, index: RaptorIndex, llm_client=None):
        self.index = index
        self.llm_client = llm_client
        self.system_prompt = """
Ты — V-AFE AI Instructor, экспертный инструктор по кайтбордингу.
Твои ответы основаны на физической базе знаний VORTEX: APPARENT FLOW ENGINE.

Отвечай:
- Инженерным, лаконичным языком
- С ссылками на конкретные концепты из базы знаний
- С акцентом на физику (векторы, силы, энергия) и механику (техника выполнения)

База знаний:
{context}

Вопрос пользователя: {question}
"""
    
    def query(
        self, 
        question: str, 
        top_k: int = 3,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Запрос к RAG-системе
        
        Args:
            question: вопрос пользователя
            top_k: количество контекстных узлов
            use_llm: использовать ли LLM для генерации
            
        Returns:
            Ответ с контекстом
        """
        # Поиск релевантного контекста
        context_nodes = self.index.retrieve(question, top_k=top_k)
        
        # Формирование контекста
        context = "\n\n".join([
            f"[{node['metadata'].get('concept_name', node['id'])}]\n"
            f"Физика: {node['metadata'].get('physics', '')}\n"
            f"Механика: {node['metadata'].get('mechanics', '')}"
            for node in context_nodes
        ])
        
        if use_llm and self.llm_client:
            # Генерация ответа через LLM
            prompt = self.system_prompt.format(
                context=context,
                question=question
            )
            response = self.llm_client.generate(prompt)
        else:
            # Простой ответ на основе контекста
            response = self._generate_simple_answer(question, context_nodes)
        
        return {
            'question': question,
            'answer': response,
            'context': context_nodes,
            'sources': [
                {
                    'id': node['metadata'].get('concept_id'),
                    'tag': node['metadata'].get('tag'),
                    'concept': node['metadata'].get('concept_name')
                }
                for node in context_nodes
            ]
        }
    
    def _generate_simple_answer(
        self, 
        question: str, 
        context_nodes: List[Dict]
    ) -> str:
        """Простая генерация ответа без LLM"""
        if not context_nodes:
            return "Не найдено релевантных концептов в базе знаний."
        
        concepts = [
            node['metadata'].get('concept_name', 'Unknown')
            for node in context_nodes
        ]
        
        return (
            f"По вашему вопросу найдено {len(context_nodes)} релевантных концептов:\n\n"
            + "\n".join(f"- {c}" for c in concepts)
            + "\n\nОбратитесь к базе знаний v-afe_core.json для деталей."
        )
