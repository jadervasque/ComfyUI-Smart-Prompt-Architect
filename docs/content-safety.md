# Segurança e autoria de conteúdo

O catálogo oficial:

- descreve sujeitos humanos como adultos;
- exclui idade ambígua e sexualização de menores;
- permite moda adulta não explícita somente em `fashion-mature`;
- limita horror a atmosfera não gráfica em `dark-atmospheric`;
- não usa celebridades, artistas, personagens, marcas ou propriedades intelectuais;
- usa descritores observáveis e não hierárquicos para pele, cabelo e traços;
- não faz rede nem carrega conteúdo remoto.

## Wildcards locais

`scripts/audit_wildcards.py` lê somente a raiz fixa
`E:\ComfyUI\ComfyUI\wildcards` no ambiente de desenvolvimento. O audit atual encontrou categorias
úteis para câmera, fundo, cor, olhos, cabelo, roupa, lugar e tempo. Foram descartados:

- `artist-horror` e `star`: nomes próprios e celebridades;
- conteúdo gráfico de `creature`, `horroroutfit` e cenas semelhantes;
- listas sensuais com formulações ambíguas ou multi-dimensionais;
- marcas de roupa/calçado e referências potencialmente protegidas;
- prompts `pos`/`neg` baseados em clichês como “masterpiece”;
- frases longas que já misturam corpo, roupa, pose e cenário.

Nenhuma linha da coleção é conteúdo oficial. A fonte autoral é
`scripts/generate_catalog.py`.

## Revisão

Todo novo pack deve passar pelo schema, auditor de duplicatas e validador semântico. Conteúdo que
exija interpretação jurídica ou política adicional deve permanecer fora do catálogo geral até
revisão humana.
