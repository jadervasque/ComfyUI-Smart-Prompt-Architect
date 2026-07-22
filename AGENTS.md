# AGENTS.md

## Missão

Implementar e manter o Prompt Architect como custom node público, seguro, determinístico e profissional para ComfyUI.

## Fonte de verdade

1. Leia `PLAN0-STATUS.md`.
2. Execute a próxima etapa elegível de `PLAN0.md`.
3. Atualize `PLAN0-STATUS.md` antes e depois do trabalho.

## Regras obrigatórias

- Use a API V3 pública do ComfyUI.
- Mantenha o core independente de ComfyUI e do frontend.
- Não use `eval`, `exec`, `pickle`, subprocessos ou instalação em runtime.
- Não faça acesso de rede durante a execução do nó.
- Não aceite caminhos arbitrários ou traversal.
- Preserve determinismo: mesma configuração e seed, mesmo resultado.
- Nunca retorne prompt positivo vazio silenciosamente.
- Não descarte valor fixo do usuário sem erro explícito.
- Não adicione dependência de runtime sem justificativa registrada.
- Não altere schemas ou comportamento público sem versionamento.
- Não publique release ou Registry sem autorização explícita.

## Qualidade

- Type hints em APIs públicas.
- Testes para toda regra e correção.
- Core com cobertura alvo de 90%.
- Execute lint, tipagem e testes antes de concluir uma etapa.
- Registre comandos e resultados reais em `PLAN0-STATUS.md`.
- Mantenha funções pequenas e responsabilidades separadas.
- Atualize documentação junto com o código.

## Git

- Use branches curtas.
- Use Conventional Commits.
- Não misture refatoração ampla com nova funcionalidade.
- Não marque etapa `DONE` sem cumprir seus critérios de aceite.

## Ao encontrar ambiguidade

Escolha a opção mais simples, segura e compatível com `PLAN0.md`; registre a decisão no Decision Log. Não invente resultado de teste nem compatibilidade.
