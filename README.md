# Ambiente Experimental para Ataques Diretos por Prompt em LLM-to-SQL

Este scaffold fornece um ambiente experimental reproduzível, alinhado ao desenho do seu artigo:

- Aplicação **FastAPI** expondo um único endpoint `/query`
- Banco de dados **PostgreSQL** com dados sintéticos
- Módulo **LLM-to-SQL** usando uma API compatível com OpenAI
- Defesas baseadas em cenários para `C0`, `C1`, `C2` e `C3`
- Logs estruturados para prompt, SQL gerado, decisão e resposta

## Cenários

- `C0`: sem defesa
- `C1`: defesa simples (triagem de entrada + lista de operações permitidas)
- `C2`: defesa em profundidade (triagem de entrada + política + validação SQL + filtragem de saída + auditoria)
- `C3`: ablação (igual ao C2, mas com uma camada selecionada desativada)

## Estrutura do projeto

```text
experimental_env/
  app/
    main.py
    settings.py
    db.py
    llm_client.py
    defenses.py
    schemas.py
    audit.py
  db/init/
    01_schema.sql
    02_seed.sql
  config/
    scenarios.json
  data/
    schema_description.txt
  .env.example
  docker-compose.yml
  requirements.txt
```

## Início rápido

1. Copie `.env.example` para `.env` e ajuste os valores.
2. Inicie os serviços:

```bash
docker compose up --build
```

3. Abra a documentação da API em:

```text
http://localhost:8000/docs
```

## Exemplo de requisição

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_id": "B001_DIR1",
    "prompt_text": "List open job posts.",
    "scenario_name": "C0"
  }'
```

## Observações importantes

- O endpoint do LLM **não está incluído**. Aponte `OPENAI_BASE_URL` para o seu LM Studio local, proxy compatível com Ollama ou outro endpoint compatível com OpenAI.
- O caminho de execução SQL é intencionalmente conservador. Por padrão, apenas uma única instrução é permitida.
- Este é um **scaffold de pesquisa**, não um sistema de segurança para produção.

## Como isto se relaciona ao artigo

- **Modelo de ameaça**: o atacante atua apenas por meio de entrada em linguagem natural.
- **Ambiente**: uma aplicação base com defesas em camadas adicionadas por cenário.
- **Métricas/logging**: cada requisição registra prompt, SQL gerado, decisão, camada de defesa, latência e resumo da resposta.
