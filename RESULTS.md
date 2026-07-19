# Resultados consolidados

## Modelo principal — LLaMA 3 8B Instruct

| Cenário | ASR operacional | Bloqueio | Erro de requisição | Latência média |
|---|---:|---:|---:|---:|
| C0 | 53,09% | 0,00% | 34,57% | 6.272,07 ms |
| C1 | 29,63% | 51,54% | 10,19% | 4.944,16 ms |
| C2 | 13,27% | 74,38% | 9,26% | 5.772,43 ms |

## Estudo de ablação

| Configuração | ASR operacional | Bloqueio | Redaction Rate |
|---|---:|---:|---:|
| C2 completo | 13,27% | 74,38% | 20,93% |
| Sem Policy Enforcement | 36,42% | 26,85% | 12,71% |
| Sem SQL Validation | 29,94% | 51,54% | 53,61% |
| Sem Output Filtering | 13,58% | 74,07% | 0,00% |

## Comparação no cenário C2

| Modelo | ASR | Bloqueio | DB Error | Latência média |
|---|---:|---:|---:|---:|
| LLaMA 3 8B Instruct | 13,27% | 74,38% | 0,00% | 5.772,43 ms |
| Mistral 7B Instruct | 37,35% | 41,05% | 9,26% | 8.449,56 ms |
| Llama 2 13B Chat | 11,42% | 85,49% | 1,85% | 17.197,51 ms |

## Interpretação

Os resultados representam uma análise descritiva realizada em um ambiente
sintético. A ASR corresponde à proporção de consultas permitidas e
classificadas como coerentes ou parcialmente coerentes com a categoria do
ataque.