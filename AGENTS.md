# AGENTS.md

## Missão

Implementar e manter o Prompt Architect como custom node público, seguro, determinístico e profissional para ComfyUI.

## Fonte de verdade

1. Use o código, os testes e os schemas versionados como contrato executável.
2. Use `README.md`, `MANUAL.md` e `docs/` como documentação pública do comportamento.
3. Trate a solicitação atual do usuário como escopo da implementação.
4. Mantenha código, testes e documentação sincronizados na mesma entrega.

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
- Mantenha funções pequenas e responsabilidades separadas.
- Atualize documentação junto com o código.

## Git

- Use branches curtas.
- Use Conventional Commits.
- Não misture refatoração ampla com nova funcionalidade.
- Nunca implemente diretamente na `master`.
- Após cada implementação validada, faça commit, publique a branch e abra um pull request para a `master`.
- Faça merge somente após os checks obrigatórios passarem e confirme que a `master` local e remota estão sincronizadas.
- Não considere a implementação concluída enquanto o pull request não estiver mesclado, salvo bloqueio explícito de revisão, permissão ou CI.

## Ao encontrar ambiguidade

Escolha a opção mais simples, segura e compatível com a arquitetura e os contratos públicos. Registre decisões relevantes na documentação ou no pull request. Não invente resultado de teste nem compatibilidade.
