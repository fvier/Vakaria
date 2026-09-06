"""
🚀 Gemini Quickstart (Python)

Este script demonstra como integrar rapidamente a API do Gemini utilizando o SDK oficial atualizado (google-genai).
Cobre:
1. Configuração básica do cliente.
2. Chamadas de geração de texto simples.
3. Respostas em tempo real (Streaming).
4. Saídas Estruturadas (Structured Outputs) com Pydantic e JSON Schema.

Pré-requisitos:
    pip install google-genai pydantic

Uso:
    export GEMINI_API_KEY="sua_chave_api_aqui"
    python gemini_quickstart.py
"""

import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. Inicialização do Cliente
# O SDK automaticamente busca a chave na variável de ambiente GEMINI_API_KEY
if "GEMINI_API_KEY" not in os.environ:
    print("⚠️  Aviso: GEMINI_API_KEY não encontrada no ambiente. Certifique-se de defini-la antes de rodar.")

client = genai.Client()
MODEL_ID = "gemini-2.5-flash"  # Recomendado para a maioria das tarefas gerais de texto/multimodal


def generate_simple_text():
    """Geração de texto simples e direta."""
    print("\n--- 1. Geração de Texto Simples ---")
    response = client.models.generate_content(
        model=MODEL_ID,
        contents="Explique em uma frase o que é Model Context Protocol (MCP).",
    )
    print(response.text)


def generate_streaming_text():
    """Geração com resposta em streaming (útil para UX interativo)."""
    print("\n--- 2. Geração em Streaming ---")
    response = client.models.generate_content_stream(
        model=MODEL_ID,
        contents="Escreva um parágrafo poético sobre inteligência artificial e criatividade.",
    )
    for chunk in response:
        print(chunk.text, end="", flush=True)
    print()


# Definição do schema desejado para a saída estruturada
class RecipeInfo(BaseModel):
    recipe_name: str = Field(description="Nome da receita culinária")
    ingredients: list[str] = Field(description="Lista de ingredientes necessários")
    prep_time_minutes: int = Field(description="Tempo de preparo estimado em minutos")
    difficulty: str = Field(description="Nível de dificuldade: Fácil, Médio ou Difícil")


def generate_structured_output():
    """Geração com retorno estruturado no formato JSON/Pydantic."""
    print("\n--- 3. Saída Estruturada (Pydantic/JSON) ---")
    
    prompt = "Crie uma receita rápida de Pão de Queijo de frigideira."
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            # Força o modelo a responder estritamente de acordo com a classe Pydantic
            response_mime_type="application/json",
            response_schema=RecipeInfo,
            system_instruction="Você é um assistente culinário focado em receitas rápidas.",
            temperature=0.2,
        ),
    )
    
    # O texto da resposta virá como uma string JSON válida contendo o schema do RecipeInfo
    print("Resposta JSON Raw:")
    print(response.text)


if __name__ == "__main__":
    try:
        # Se você quiser rodar para testar, descomente as funções abaixo
        # generate_simple_text()
        # generate_streaming_text()
        # generate_structured_output()
        print("Receita carregada com sucesso! Descomente as funções no bloco __main__ para executar testes rápidos.")
    except Exception as e:
        print(f"Erro ao executar a receita: {e}")
