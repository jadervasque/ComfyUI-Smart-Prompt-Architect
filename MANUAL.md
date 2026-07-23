# Manual do Prompt Architect

Este manual descreve o uso do Prompt Architect no ComfyUI. Na versão atual existe um único nó
público:

- **Nome visível:** `Prompt Architect`
- **Categoria:** `Prompt Architect → Generation`
- **ID interno:** `PromptArchitect_PromptArchitect`

O nó compõe prompts positivos e negativos a partir de perfis e bibliotecas validados. Ele não
carrega modelos, não usa GPU, não consulta serviços externos durante a execução e produz o mesmo
resultado quando recebe a mesma configuração, seed, índice de batch e versão dos dados.

## 1. Primeiro uso

1. Inicie ou reinicie o ComfyUI depois de instalar ou atualizar o custom node.
2. No canvas, clique duas vezes em uma área vazia e busque por `Prompt Architect`.
3. Adicione o nó encontrado em `Prompt Architect → Generation`.
4. Mantenha inicialmente:
   - `profile`: `portrait`;
   - `seed`: `0` ou outra seed não negativa;
   - `generation_mode`: `balanced`;
   - `strict_validation`: ativado;
   - `identity_lock`: ativado;
   - `configuration_json`: `{}`.
5. Clique em **Open Architect** para abrir o editor visual.
6. Na aba **Preview & JSON**, clique em **Generate preview**.
7. Confira os prompts positivo e negativo.
8. Clique em **Save configuration**. Preview, Import, Export e Apply advanced JSON não salvam o
   nó por conta própria.
9. Conecte `positive_prompt` e `negative_prompt` ao restante do workflow.
10. Execute a fila normalmente.

### Ligação típica com os nós de texto do ComfyUI

Uma ligação comum é:

1. Adicione dois nós `CLIP Text Encode (Prompt)`, um para positivo e outro para negativo.
2. Se o campo `text` desses nós ainda for um widget, converta-o em entrada usando a opção de
   conversão de widget do ComfyUI.
3. Ligue `positive_prompt` ao `text` do encoder positivo.
4. Ligue `negative_prompt` ao `text` do encoder negativo.
5. Ligue a saída `CLIP` de um loader de checkpoint aos dois encoders.
6. Ligue os conditionings positivo e negativo ao sampler usado no workflow.

O nome da ação de conversão do widget pode variar entre versões do frontend. Também é possível
usar qualquer nó intermediário que aceite `STRING`.

## 2. Perfis incluídos

O perfil define quais campos existem, sua ordem, seus padrões, fallbacks e o template final.

| Perfil | Quando usar | Comportamento principal |
|---|---|---|
| `portrait` | Retratos fotográficos gerais | Sujeito fixo por padrão; aparência, pose, cenário, câmera e qualidade variam de forma compatível. |
| `virtual-model` | Personagem ou modelo virtual consistente | Inclui grupo de identidade mais completo, boca, corpo e roupa; combina bem com seed explícita no grupo `identity`. |
| `dataset` | Séries reproduzíveis para datasets | Mantém sujeito, identidade e qualidade fixos por padrão; `batch_index` varia os demais campos sem estado oculto. |

Trocar o perfil dentro do editor reinicia as configurações de campo. Se houver valores em modo
`fixed` ou `custom`, o editor pede confirmação antes de descartá-los.

## 3. Entradas do nó

### `profile`

Seleciona o perfil de composição. Os valores incluídos são `portrait`, `virtual-model` e
`dataset`.

- O perfil controla campos, ordem de composição, bibliotecas, regras, fallbacks e tamanho mínimo.
- Um `profile_override_json`, quando fornecido, deve ter o mesmo ID do perfil selecionado.
- Trocar o perfil pode invalidar IDs de opções pertencentes ao perfil anterior.

### `seed`

É a master seed usada para derivar seeds independentes para grupos e seções.

- Deve ser um inteiro não negativo.
- O backend aceita até `2^64 - 1`.
- Para portabilidade no editor e no JSON do navegador, prefira valores de `0` a
  `9.007.199.254.740.991`, o maior inteiro seguro do JavaScript.
- Mesma seed e mesma configuração produzem a mesma saída.
- Alterar a seed normalmente altera todos os grupos que não possuem seed explícita bloqueada.
- O controle de seed do ComfyUI pode ser configurado para mudar depois de cada geração.

### `generation_mode`

Seleciona a estratégia determinística de seleção.

| Modo | Efeito atual |
|---|---|
| `strict` | Respeita filtros de tags sem relaxamento. Se filtros e regras eliminarem todas as opções, usa fallback válido ou falha claramente. |
| `balanced` | Padrão recomendado. Se os filtros de tags eliminarem todas as opções, tenta novamente sem esses filtros, mantendo as regras absolutas. O relaxamento é registrado. |
| `creative` | Tem o mesmo relaxamento de tags do modo balanced e reduz a influência das preferências de peso, aumentando a diversidade. Regras absolutas continuam obrigatórias. |
| `dataset` | Identifica uma composição voltada a dataset e fica disponível para regras declarativas. Não relaxa filtros de tags; use `batch_index` para variação explícita. |
| `sequential` | Identifica uma composição sequencial e fica disponível para regras. Não mantém contador oculto: a sequência é controlada por `batch_index`. |

Todos os modos são determinísticos. Nenhum modo pode sobrescrever silenciosamente um valor fixado
pelo usuário ou permitir prompt positivo vazio.

### `strict_validation`

É mantido no schema para clareza e compatibilidade de workflows.

Na versão atual, toda validação de segurança é obrigatória mesmo quando esse controle é desativado.
Portanto, desativá-lo não permite prompt vazio, seção obrigatória ausente, referência inválida ou
conflito com valor fixo. Recomenda-se deixá-lo ativado.

### `identity_lock`

Controla o bloqueio do grupo `identity`.

- Ativado sem seed explícita: o nó deriva uma seed de identidade a partir da master seed. Isso é
  determinístico para a mesma master seed.
- Ativado com seed explícita no grupo `identity`: a identidade permanece estável mesmo quando a
  master seed muda.
- Desativado: qualquer seed armazenada no grupo deixa de prevalecer e o grupo volta a ser derivado
  da master seed.

Para criar várias imagens da mesma pessoa com roupa, pose e cenário diferentes, ative o lock e
preencha uma seed explícita para `identity` na aba **Groups**.

### `configuration_json`

Armazena o estado portátil do editor dentro do workflow. O botão **Open Architect** usa esse JSON
como fonte de verdade para campos, filtros e grupos.

- `{}` usa os padrões do nó e do perfil.
- O limite é 262.144 bytes em UTF-8.
- A raiz deve ser um objeto JSON.
- Campos desconhecidos e versões incompatíveis são rejeitados.
- Não coloque comentários, `NaN`, caminhos de arquivo ou código no JSON.
- Use preferencialmente o editor visual; edite manualmente somente quando necessário.

Os controles visíveis do nó têm precedência sobre os campos básicos equivalentes do JSON:

- `profile` substitui `profile_id`;
- `generation_mode` substitui `mode`;
- `seed` substitui `master_seed`;
- `batch_index` substitui `batch_index`;
- `identity_lock` substitui `groups.identity.locked`;
- os quatro controles de prefixo/sufixo substituem `overrides`;
- `external_context_json` substitui os campos correspondentes por valores fixos.

Seeds explícitas dos grupos e configurações dos demais campos continuam vindo de
`configuration_json`.

### `positive_prefix`

Texto inserido antes do prompt positivo gerado.

Use para instruções globais que devem aparecer em todas as composições, por exemplo:

```text
professional editorial photograph
```

O prefixo é combinado e normalizado; ele não substitui o conteúdo criado pelo perfil.

### `positive_suffix`

Texto inserido depois do prompt positivo gerado. Pode ser usado para acabamento ou instruções
globais, por exemplo:

```text
natural color grading, restrained post-processing
```

### `negative_prefix`

Texto inserido antes do prompt negativo gerado, por exemplo:

```text
low quality, oversaturated
```

### `negative_suffix`

Texto inserido depois do prompt negativo gerado, por exemplo:

```text
watermark, text, logo
```

Os quatro controles de prefixo/sufixo passam pela normalização final de espaços e pontuação.

### `profile_override_json` — avançado

Aceita um objeto JSON completo de perfil para substituir, somente nessa execução, o perfil
selecionado.

- É conteúdo JSON, não caminho de arquivo.
- O ID do override deve ser igual ao valor de `profile`.
- O limite é 262.144 bytes.
- O schema deve ser `1.0`.
- Templates, seções, IDs e referências são validados antes da composição.
- O nó não executa Python, expressões ou comandos presentes no conteúdo.
- As bibliotecas referenciadas precisam estar disponíveis no repositório de dados do nó.

Para autoria de perfis, consulte [docs/configuration.md](docs/configuration.md) e os schemas em
[`prompt_architect/data/schemas`](prompt_architect/data/schemas).

### `external_context_json` — avançado

Aceita um objeto que mapeia IDs de seção para IDs de opção. Cada entrada se torna um valor
`fixed` e prevalece sobre a configuração desse campo.

Exemplo:

```json
{
  "subject": "adult-woman",
  "outfit": "formal-suit",
  "location": "neutral-studio"
}
```

Use essa entrada para receber decisões de outros nós ou para integrar o Prompt Architect a uma
configuração externa. Chaves ou valores inválidos geram erro explícito; um valor fixo nunca é
descartado silenciosamente.

### `batch_index` — avançado

Índice inteiro não negativo incorporado à seed de cada seção.

- Mesma master seed e mesmo índice produzem a mesma composição.
- Alterar somente o índice produz uma variação reproduzível.
- É especialmente útil com os modos `dataset` e `sequential`.
- Não existe incremento interno oculto. Para uma sequência, altere ou conecte explicitamente o
  índice em cada item.

## 4. Editor visual: `Open Architect`

O editor possui quatro abas. Alterações dentro dele permanecem temporárias até clicar em
**Save configuration**.

### Aba `Basic`

Contém:

- **Profile:** mesmo controle de `profile` do nó.
- **Generation mode:** mesmo controle de `generation_mode`.
- **Master seed:** mesmo controle de `seed`.
- **Batch index:** mesmo controle avançado do nó.
- **Keep identity group locked:** sincronizado com `identity_lock`.
- **Positive/Negative prefix/suffix:** sincronizados com os quatro controles de texto do nó.
- **Reset selected profile:** restaura o perfil selecionado para `balanced`, seed `0`, batch `0`,
  identity lock ativado, campos vazios e prefixos/sufixos vazios. Exige confirmação.

Ao abrir o editor, o valor atualmente visível de `identity_lock` no nó prevalece sobre uma cópia
antiga em `configuration_json`. O checkbox **Keep identity group locked** e o controle
**Groups > identity > Lock group** permanecem vinculados: alterar qualquer um atualiza o outro, e
**Save configuration** grava o mesmo valor de volta no widget do nó e no JSON.

### Aba `Fields`

Mostra um cartão para cada seção do perfil. Cada cartão informa o ID, o grupo e se a seção é
obrigatória.

#### `Mode`

| Modo do campo | O que faz |
|---|---|
| `inherit` | Usa o modo e o valor padrão definidos pelo perfil. É a melhor opção quando você não precisa de override. |
| `random` | Escolhe deterministicamente uma opção elegível da biblioteca, considerando pesos, tags, regras, seed do grupo e batch index. |
| `fixed` | Exige uma opção em `Value` e preserva essa escolha. Regras não podem trocá-la silenciosamente. |
| `custom` | Exibe `Custom text` para escrever exatamente o que esta seção deve acrescentar ao prompt, sem exigir uma opção da biblioteca. |
| `disabled` | Omite uma seção opcional. Desativar uma seção obrigatória causa erro explícito. |

#### `Value`

Fica habilitado somente em modo `fixed`. A lista mostra o texto das opções, enquanto o JSON salva
o ID estável da opção.

#### `Custom text`

Aparece somente em modo `custom`. Digite uma descrição não vazia, de até 4.096 caracteres,
específica para aquele campo. O texto é salvo no próprio workflow, participa da normalização final
e é registrado no manifesto com origem `custom`. Ele não precisa existir na biblioteca e não é
alterado pela seed. Regras não podem substituí-lo silenciosamente; se uma combinação customizada
violar uma regra absoluta de outra opção, o preview retorna um erro explícito.

Exemplo no campo `outfit`:

```text
They wear a bespoke emerald coat with brass buttons
```

Os filtros `Include tags` e `Exclude tags` só afetam o modo `random`; eles não modificam texto
customizado.

#### `Include tags`

Lista separada por vírgulas. Uma opção só é elegível quando contém **todas** as tags incluídas.
Tags são normalizadas para minúsculas, deduplicadas e ordenadas.

Exemplo:

```text
portrait, natural
```

#### `Exclude tags`

Lista separada por vírgulas. Uma opção é removida quando contém **qualquer** tag excluída.

Se os filtros eliminarem todas as opções:

- `balanced` e `creative` podem relaxar apenas os filtros de tags e registrar o evento;
- `strict`, `dataset` e `sequential` mantêm os filtros;
- regras de compatibilidade absolutas nunca são relaxadas;
- o motor usa um fallback válido ou retorna erro.

### Aba `Groups`

Agrupa campos que devem compartilhar uma origem determinística independente. Perfis atuais usam
grupos como `identity`, `appearance`, `outfit`, `pose`, `scene`, `lighting`, `camera`, `quality` e
`negative`.

Cada grupo possui:

- **Lock group:** permite que uma seed explícita prevaleça sobre a derivação da master seed.
- **Explicit seed:** seed usada quando o grupo está bloqueado. Em branco, a seed é derivada da
  master seed.

No grupo `identity`, **Lock group** representa exatamente o mesmo estado de `identity_lock` no nó
e de **Keep identity group locked** na aba Basic.

Exemplo para manter identidade e variar o restante:

1. Escolha `virtual-model`.
2. Na aba **Groups**, localize `identity`.
3. Marque **Lock group**.
4. Defina **Explicit seed** como `4242`.
5. Deixe os demais grupos sem lock ou sem seed explícita.
6. Salve.
7. Varie a master seed ou o batch index. Os campos do grupo `identity` permanecem estáveis.

Uma seed preenchida em um grupo desbloqueado é ignorada durante a seleção; ative o lock para que
ela seja usada.

### Aba `Preview & JSON`

#### `Generate preview`

Executa a mesma pipeline autoritativa do nó, mas sem enfileirar o workflow.

- Usa inclusive alterações ainda não salvas no modal.
- Mostra os prompts positivo e negativo.
- Mostra o manifesto completo em **Manifest**.
- Não grava arquivos e não altera o workflow.

Depois de aprovar o preview, clique em **Save configuration** antes de fechar o editor ou executar
a fila.

#### `Manifest`

Exibe o registro de reprodutibilidade da composição:

- versões do engine, perfil e bibliotecas;
- hash da configuração efetiva;
- master seed e seeds de grupos;
- opção e origem de cada seção;
- tentativas, regras, conflitos resolvidos, fallbacks e warnings;
- prompts finais.

#### `Advanced JSON`

Permite editar diretamente a configuração portátil. Exemplo mínimo completo:

```json
{
  "batch_index": 0,
  "fields": {
    "subject": {
      "exclude_tags": [],
      "include_tags": [],
      "mode": "fixed",
      "value": "adult-woman"
    }
  },
  "groups": {
    "identity": {
      "locked": true,
      "seed": 4242
    }
  },
  "master_seed": 123,
  "mode": "balanced",
  "overrides": {
    "negative_prefix": "",
    "negative_suffix": "watermark, logo",
    "positive_prefix": "professional editorial photograph",
    "positive_suffix": ""
  },
  "profile_id": "virtual-model",
  "profile_version": "1.0.0",
  "schema_version": "1.1"
}
```

Clique em **Apply advanced JSON** para validar o texto e atualizar as outras abas. Isso ainda não
grava o nó; finalize com **Save configuration**.

#### `Import JSON`

Importa um arquivo `.json` de configuração de até 262.144 bytes, valida e atualiza o editor. O
arquivo não pode conter caminhos ou código executável.

#### `Export JSON`

Baixa a configuração atual como:

```text
prompt-architect-<profile>.json
```

O export coleta o estado atual de todas as abas, inclusive alterações ainda não salvas no nó.

### Botões de fechamento e salvamento

- **Save configuration:** grava `configuration_json`, controles básicos, prefixos/sufixos e batch
  index no nó; marca o workflow como alterado.
- **Cancel**, `×`, `Esc` ou clique fora do modal: fecham o editor sem aplicar o estado temporário ao
  nó.

## 5. Campos disponíveis

Nem todos os perfis usam todos os campos.

| Campo | Finalidade | Perfis |
|---|---|---|
| `subject` | Tipo de sujeito adulto | Todos |
| `identity` | Características gerais de identidade | `virtual-model`, `dataset` |
| `face` | Formato e características faciais | Todos |
| `eyes` | Aparência dos olhos | Todos |
| `mouth` | Aparência/posição da boca | `virtual-model` |
| `skin` | Textura e tonalidade da pele | Todos |
| `hair-color` | Cor do cabelo | `portrait`, `virtual-model` |
| `hair-length` | Comprimento do cabelo | Todos |
| `hair-texture` | Textura do cabelo | `portrait`, `virtual-model` |
| `hair-style` | Penteado compatível com o comprimento | Todos |
| `body` | Constituição corporal adulta | `virtual-model` |
| `outfit` | Roupa | `virtual-model`, `dataset` |
| `expression` | Expressão facial | Todos |
| `pose` | Pose | Todos |
| `location` | Cenário ou local | Todos |
| `lighting` | Iluminação | Todos |
| `camera` | Perspectiva e lente | Todos |
| `composition` | Enquadramento | Todos |
| `quality` | Diretrizes de detalhe e realismo | Todos |
| `negative` | Termos negativos | Todos |

## 6. Saídas do nó

### `positive_prompt` — `STRING`

Prompt positivo final, normalizado e validado. Nunca é retornado vazio silenciosamente.

### `negative_prompt` — `STRING`

Prompt negativo final. Os três perfis incluídos exigem conteúdo negativo válido.

### `manifest_json` — `STRING`

JSON canônico para auditoria e reprodução. Pode ser ligado a um nó de exibição ou salvamento de
texto. Não contém caminho absoluto da instalação.

### `summary` — `STRING`

Resumo curto com perfil, seed, quantidade de seções, tentativas, fallbacks e warnings. É útil para
debug, logs e metadados sem transportar o manifesto inteiro.

### `seed_used` — `INT`

Master seed efetivamente usada. Pode ser exibida, salva como metadado ou conectada a outro nó que
aceite inteiro.

## 7. Receitas práticas

### Retrato rápido

1. Selecione `portrait`.
2. Use `balanced`.
3. Defina uma seed.
4. No editor, mantenha os campos em `inherit`.
5. Gere o preview e salve.
6. Conecte os dois prompts aos encoders positivo e negativo.

### Modelo virtual consistente em várias imagens

1. Selecione `virtual-model`.
2. Em **Groups**, bloqueie `identity` com seed explícita, por exemplo `4242`.
3. Deixe `outfit`, `pose`, `scene`, `lighting` e `camera` derivados.
4. Salve a configuração.
5. Varie a master seed ou o batch index entre imagens.
6. Verifique `manifest_json` para confirmar que a seed do grupo `identity` não mudou.

Esse lock estabiliza as escolhas textuais de identidade. Ele não garante sozinho consistência
visual do modelo generativo; combine-o com as técnicas de condicionamento adequadas ao seu
workflow.

### Série determinística para dataset

1. Selecione `dataset`.
2. Escolha `generation_mode = dataset` ou `sequential`.
3. Mantenha a master seed fixa.
4. Comece com `batch_index = 0`.
5. Para cada item, use índices `1`, `2`, `3` e assim por diante.
6. Armazene `manifest_json`, `seed_used` e o índice junto da imagem.

Reutilizar master seed e índice reproduz a mesma composição. O índice precisa ser alterado pelo
workflow ou pelo usuário; o nó não mantém contador entre execuções.

### Fixar roupa e cenário externamente

Use em `external_context_json`:

```json
{
  "outfit": "casual-jacket",
  "location": "urban-street"
}
```

Escolha IDs existentes no perfil. Se uma regra tornar a combinação impossível, o nó relata o
conflito em vez de substituir os valores.

### Filtrar opções por tags

1. Abra **Fields**.
2. Coloque o campo em `random`.
3. Preencha **Include tags** com todas as características obrigatórias.
4. Preencha **Exclude tags** com características proibidas.
5. Use `strict` para nunca relaxar os filtros ou `balanced` para permitir recuperação quando o
   filtro ficar sem candidatos.
6. Gere preview e confira o manifesto.

### Escrever um valor fora da biblioteca

1. Abra **Fields**.
2. Localize o grupo específico, por exemplo `outfit`, `pose` ou `location`.
3. Em **Mode**, escolha `custom`.
4. No campo **Custom text** que aparecer, descreva exatamente o resultado desejado.
5. Gere o preview e confira a integração do texto com as demais seções.
6. Clique em **Save configuration**.

O valor customizado pertence somente ao campo em que foi escrito. Outros campos continuam usando
`inherit`, `random`, `fixed` ou `disabled` conforme suas próprias configurações.

## 8. Determinismo e cache

O resultado depende de:

- versão do engine;
- versão do perfil e das bibliotecas;
- configuração efetiva;
- master seed;
- seeds explícitas de grupos;
- batch index.

O nó inclui seus inputs e o conteúdo dos JSONs empacotados no fingerprint de cache. Alterar uma
entrada ou atualizar dados oficiais invalida corretamente a execução armazenada pelo ComfyUI.

Mesmo perfil, configuração, seed, índice e versão produzem prompt e manifesto idênticos. Atualizar
o custom node pode mudar versões ou dados; mantenha o manifesto quando a reprodução exata for
importante.

## 9. Erros e solução de problemas

### O nó não aparece na busca

1. Confirme que a pasta está dentro de `ComfyUI/custom_nodes`.
2. Reinicie completamente o ComfyUI.
3. Busque por `Prompt Architect`.
4. Procure `ComfyUI-Smart-Prompt-Architect` na tabela **Import times for custom nodes** do log.
5. Se houver traceback logo antes dessa tabela, corrija o primeiro erro do traceback.

### O botão `Open Architect` não aparece

1. Confirme que o nó Python aparece e executa.
2. Faça recarregamento completo da página do ComfyUI.
3. Limpe o cache do frontend se os assets antigos continuarem carregados.
4. Reinicie o servidor depois de atualizar o custom node.

### Preview funciona, mas a fila usa outra configuração

O preview usa o estado temporário do modal. Clique em **Save configuration** antes de fechar ou
enfileirar. **Apply advanced JSON** atualiza somente o editor.

### `Invalid configuration JSON`

- Remova comentários e vírgulas finais.
- Verifique se a raiz é `{ ... }`, não uma lista.
- Use aspas duplas em chaves e strings.
- Não use valores `NaN` ou `Infinity`.
- Restaure com **Reset selected profile** se não precisar preservar overrides.

### `unknown fields` ou `unsupported schema version`

O contrato é estrito. Use `schema_version: "1.1"` nas novas configurações. Configurações `1.0`
continuam legíveis, mas o modo `custom` exige `1.1`. Não acrescente propriedades arbitrárias ao
JSON.

### `fixed section ... references unknown option`

O valor fixo não existe na biblioteca do perfil atual. Selecione novamente o valor na aba
**Fields** ou remova o override para voltar a `inherit`.

### `required section ... cannot be disabled`

Uma seção obrigatória foi configurada como `disabled`. Volte para `inherit`, `random`, `fixed` ou
`custom`.

### Nenhuma opção ou fallback válido

Filtros ou regras eliminaram todas as opções.

1. Remova tags excessivamente restritivas.
2. Confira combinações fixas incompatíveis.
3. Teste `balanced` para permitir relaxamento de filtros de tags.
4. Examine o erro e o manifesto do último preview válido.

### A identidade muda quando a master seed muda

Marcar apenas `identity_lock` sem seed explícita ainda deriva a identidade da master seed. Na aba
**Groups**, bloqueie `identity` e defina uma **Explicit seed** fixa.

### O resultado não muda

Isso é esperado quando configuração, seed e batch index permanecem iguais. Altere a master seed,
o batch index ou uma configuração de campo. Um grupo bloqueado com seed explícita continuará
estável por definição.

### O override de perfil é rejeitado

Confirme que:

- o JSON é um objeto de perfil completo;
- `schema_version` é `1.0`;
- `id` é igual ao perfil selecionado no nó;
- todas as seções, templates, IDs e bibliotecas referenciadas são válidas;
- o conteúdo não excede 262.144 bytes.

## 10. Segurança e limites

Durante a composição, o nó:

- não acessa a internet;
- não instala pacotes;
- não executa código vindo do JSON;
- não aceita caminhos arbitrários;
- não escreve perfis ou configurações no servidor;
- rejeita traversal e IDs fora do formato permitido;
- limita inputs JSON a 262.144 bytes;
- falha explicitamente em vez de descartar valor fixo ou retornar prompt positivo vazio.

Import e Export no editor operam com arquivos escolhidos pelo navegador. A configuração efetiva é
salva no próprio workflow somente após **Save configuration**.

## 11. Referências

- [README do projeto](README.md)
- [Contrato de configuração](docs/configuration.md)
- [Perfis oficiais](docs/official-profiles.md)
- [Regras de compatibilidade](docs/rules.md)
- [Rendering e normalização](docs/rendering.md)
- [Manifesto e diagnósticos](docs/manifest.md)
- [API local de preview](docs/API.md)
- [Guia de desenvolvimento](docs/DEVELOPMENT.md)
- [Política de segurança](SECURITY.md)
