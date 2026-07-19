# Informações de reprodutibilidade

## Dataset

Arquivo: `data/04_final_prompt_dataset.csv`

SHA-256:

`a7c4888184b235823316690470f0a1e95b76fed2ea3d79288ff08fff50243534`

O arquivo é idêntico ao dataset final produzido pelo repositório de geração.

## Configuração

- PostgreSQL 16;
- API FastAPI;
- temperatura dos modelos igual a 0;
- reset do banco antes de cada requisição;
- uma execução por combinação;
- cenários C0, C1, C2 e C3;
- modelos LLaMA 3 8B Instruct, Mistral 7B Instruct v0.3 e Llama 2 13B Chat.

## Resultados

Os resultados brutos estão em `results/`.

As tabelas consolidadas estão em `results/tables_for_paper/`.
