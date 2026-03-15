"""
V-AFE API: FastAPI Backend для чат-бота
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path

from raptor_rag import RaptorIndex, VAFERAG


# === Конфигурация ===
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / ".config"

# === Pydantic модели ===


class ChatMessage(BaseModel):
    """Сообщение чата"""
    role: str  # 'user' или 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Запрос к чату"""
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    top_k: int = 3
    use_llm: bool = True


class ChatResponse(BaseModel):
    """Ответ чата"""
    answer: str
    sources: List[Dict[str, Any]]
    context_used: List[Dict[str, Any]]


class ConceptInfo(BaseModel):
    """Информация о концепте"""
    id: int
    tag: str
    concept: str
    physics: str
    mechanics: str


class KnowledgeBaseResponse(BaseModel):
    """Ответ базы знаний"""
    concepts: List[ConceptInfo]
    total: int


# === Приложение FastAPI ===

app = FastAPI(
    title="V-AFE API",
    description="API для VORTEX: Apparent Flow Engine — AI инструктор по кайтбордингу",
    version="2.0.0"
)

# CORS для GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dizel0110.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Глобальные объекты ===

rag_engine: Optional[VAFERAG] = None
index: Optional[RaptorIndex] = None
core_data: Optional[Dict] = None


def load_core_data() -> Dict:
    """Загрузка ядра знаний"""
    core_path = DATA_DIR / "v-afe_core.json"
    with open(core_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def initialize_rag():
    """Инициализация RAG-движка"""
    global rag_engine, index, core_data
    
    core_data = load_core_data()
    index = RaptorIndex(model_name='all-MiniLM-L6-v2')
    index.build_from_core(core_data)
    
    # Заглушка для LLM (можно подключить Google Gemini)
    class DummyLLM:
        def generate(self, prompt: str) -> str:
            return "[LLM ответ требует API ключа]"
    
    rag_engine = VAFERAG(index=index, llm_client=DummyLLM())


# === События lifespan ===

@app.on_event("startup")
async def startup_event():
    """Инициализация при старте"""
    initialize_rag()
    print("✓ V-AFE RAG engine initialized")


# === API Endpoints ===

@app.get("/")
async def root():
    """Информация об API"""
    return {
        "name": "V-AFE API",
        "version": "2.0.0",
        "description": "AI Instructor for Kiteboarding",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Проверка здоровья"""
    return {
        "status": "healthy",
        "rag_loaded": rag_engine is not None,
        "concepts_count": len(core_data.get('knowledge_base', [])) if core_data else 0
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Основной endpoint для чата
    
    Принимает вопрос пользователя, возвращает ответ с источниками
    """
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    
    result = rag_engine.query(
        question=request.message,
        top_k=request.top_k,
        use_llm=request.use_llm
    )
    
    return ChatResponse(
        answer=result['answer'],
        sources=result['sources'],
        context_used=result['context']
    )


@app.get("/api/knowledge-base", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(tag: Optional[str] = None):
    """
    Получение базы знаний
    
    Args:
        tag: фильтр по тегу (опционально)
    """
    concepts = core_data.get('knowledge_base', [])
    
    if tag:
        concepts = [
            c for c in concepts
            if tag.lower() in c.get('tag', '').lower()
        ]
    
    return KnowledgeBaseResponse(
        concepts=[
            ConceptInfo(
                id=c['id'],
                tag=c['tag'],
                concept=c['concept'],
                physics=c['physics'],
                mechanics=c['mechanics']
            )
            for c in concepts
        ],
        total=len(concepts)
    )


@app.get("/api/knowledge-base/{concept_id}")
async def get_concept(concept_id: int):
    """Получение конкретного концепта"""
    concepts = core_data.get('knowledge_base', [])
    
    for concept in concepts:
        if concept['id'] == concept_id:
            return concept
    
    raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")


@app.get("/api/tags")
async def get_tags():
    """Получение всех тегов"""
    concepts = core_data.get('knowledge_base', [])
    tags = set()
    
    for concept in concepts:
        tag = concept.get('tag', '')
        for t in tag.split('/'):
            tags.add(t.strip())
    
    return {"tags": sorted(list(tags))}


@app.post("/api/index/rebuild")
async def rebuild_index():
    """Перестройка индекса (после обновления базы знаний)"""
    initialize_rag()
    return {"status": "index rebuilt", "concepts": len(core_data.get('knowledge_base', []))}


# === Запуск ===

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
