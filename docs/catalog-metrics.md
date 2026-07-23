# Métricas e validação

`tests.property_profiles` gera prompts para todos os 15 perfis e mede:

- frequência por opção e família;
- cobertura e itens nunca selecionados;
- fallbacks, rejeições e tentativas;
- prompts únicos e colisões por SHA-256;
- entropia de famílias;
- top 10 opções;
- tempo e prompts por segundo.

Execução completa:

```console
python -m tests.property_profiles --seeds 10000 --output reports/catalog-metrics.json
```

O gate exige prompt positivo não vazio, zero placeholder, zero termo proibido, somente packs
habilitados, pelo menos 95% de prompts únicos e alcance de todas as opções elegíveis em 10.000
seeds. O determinismo é repetido nas primeiras 128 seeds de cada perfil e também coberto por testes
unitários e de integração.

Outros comandos:

```console
python -m scripts.benchmark --iterations 1000 --max-seconds 300
python -m scripts.catalog_stats
python -m scripts.find_catalog_duplicates
python -m scripts.validate_catalog_semantics
```

O relatório gerado é evidência, não entrada do runtime.

## Resultado de referência

Execução local em Windows, Python 3.12.10, em 2026-07-23:

- 150.000 prompts compostos, 10.000 por perfil;
- 15 de 15 perfis aprovados;
- 100% de prompts únicos em cada perfil;
- cobertura por perfil entre 99,07% e 100%;
- cobertura global de 5.184/5.184 opções ativas;
- zero opção nunca selecionada e zero fallback;
- 1.920 amostras repetidas para verificar determinismo.

Benchmark de referência:

- 15 perfis carregados em 10,901 s;
- pico de memória rastreada de 12,7 MiB;
- 15.000 composições em 252,853 s, ou 59,3 prompts/s.

Os valores de tempo e throughput dependem do hardware e do ambiente. O arquivo
`reports/catalog-metrics.json` contém as métricas detalhadas por perfil.
