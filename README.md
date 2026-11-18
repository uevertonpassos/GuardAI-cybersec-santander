# GuardAI — segurança guiada por skills

Especialização educacional do conceito de DIO Agent em **análise defensiva de vulnerabilidades**. O agente pergunta pelo contexto, explica a causa do problema e apresenta impacto, probabilidade e severidade em um formato comparável. As skills são roteiros em Markdown, escritos em português; os scripts apenas ajudam a verificar exemplos e registrar evidências.

Escolhi segurança de aplicações porque um achado só é útil quando conecta evidência, contexto, correção e teste. O projeto exercita essa sequência em código Python, configuração de serviço e infraestrutura fictícia. É um projeto independente de estudo, sem vínculo ou integração com sistemas do Santander ou da DIO. Como a base original do curso não foi fornecida, esta é uma implementação autônoma compatível com um harness de skills, não um fork declarado do material da Expert.

**Estado da entrega:** repositório local preparado, sem push e sem publicação. Nome para o GitHub: **guardai-santander**. Conta proprietária, visibilidade pública, URL e execução no GitHub Actions só poderão ser conferidas quando você publicar. Não há link de repositório público inventado.

## Comece pelo laboratório

Pré-requisitos: Python 3.10 ou superior e Git. Os exemplos e testes usam somente a biblioteca padrão, sem instalação de pacotes, servidores, chaves ou dados pessoais. A validação local foi feita com Python 3.13.

Na raiz deste projeto, execute:

```powershell
python lab/vulnerable/app.py
python lab/hardened/app.py
python -m unittest discover -s tests -v
python scripts/validate_project.py
python scripts/security_review.py --tracked
```

A busca normal retorna Ana Demo nas duas versões. A entrada adversarial local retorna duas pessoas no exemplo vulnerável e nenhuma na versão parametrizada. Os 15 testes também verificam apóstrofos legítimos, as configurações, a escala de risco, códigos de saída e a revisão de um commit Git mesmo com alterações posteriores no diretório de trabalho.

O modo `--tracked` exige arquivos no índice Git. No repositório preparado eles já estão no índice; se você obtiver apenas um ZIP, inicialize com `git init -b main` e `git add .` antes de usar esse modo. Um clone já atende esse pré-requisito.

## Como usar o agente no harness

O caminho documentado é o Codex CLI, instalado e autenticado separadamente. Abra uma sessão a partir da raiz:

```powershell
codex -C .
```

Envie:

```text
Use $analise-vulnerabilidades para revisar lab/vulnerable/app.py.
O código é meu laboratório, os dados são fictícios e autorizo leitura e
os testes locais previstos no AGENTS.md. Não use serviços externos.
Explique as evidências e compare com lab/hardened/app.py.
```

Para observar as perguntas iniciais, abra outra sessão e envie apenas “Analise este app.py”, indicando o arquivo, sem antecipar ambiente e permissão. Veja o [guia do harness](docs/harness.md) para os outros prompts e para carregar os arquivos em um harness que não descubra skills automaticamente. O agente aproveita o contexto existente; não repete perguntas já respondidas. A estrutura local segue a [documentação oficial de skills](https://learn.chatgpt.com/docs/build-skills).

## O que foi criado

Todos os arquivos foram criados neste projeto, pois a pasta estava vazia.

| Parte | Arquivo ou pasta | Finalidade |
| --- | --- | --- |
| Instruções | [AGENTS.md](AGENTS.md) | Escopo, autorização, comandos e tabela de skills |
| Persona | [persona/guardai.md](persona/guardai.md) | Mentor defensivo, didático e orientado a evidências |
| Conhecimento | [metodologia](knowledge/metodologia.md) e [referências](knowledge/referencias.md) | Escala de risco, limites e fontes primárias |
| Skill principal | [análise de vulnerabilidades](.agents/skills/analise-vulnerabilidades/SKILL.md) | Contexto → evidência → risco → correção → validação |
| Skill de testes | [testes de segurança](.agents/skills/testes-seguranca/SKILL.md) | Reprodução e regressão em laboratório autorizado |
| Skill de estudo | [trilha de cibersegurança](.agents/skills/trilha-ciberseguranca/SKILL.md) | Plano adaptado ao nível, objetivo e tempo disponível |
| Formato | [templates/relatorio.md](templates/relatorio.md) | Relatório com campos estáveis e limites explícitos |
| Exemplos | [vulnerável](lab/vulnerable/) e [corrigido](lab/hardened/) | Python, configuração e infraestrutura declarativa |
| Testes | [tests/test_security.py](tests/test_security.py) | 15 testes locais de comportamento |
| Automação | [scripts](scripts/) | Verificação estática, integridade e captura de saídas reais |
| Desenvolvimento | [workflow](.github/workflows/security.yml) e [template de PR](.github/pull_request_template.md) | Verificações por alteração e revisão humana |
| Evidências | [evidence](evidence/) | Análise, contexto, saídas e hashes dos insumos |
| Estudo | [trilha de exemplo](examples/trilha-iniciante.md) | Quatro semanas com entregas verificáveis |
| Avaliação | [roteiro manual](docs/avaliacao-manual.md) | Critérios para avaliar o comportamento das skills |

## Melhorias implementadas

1. **Testes de segurança:** comparação entre caso vulnerável e correção, incluindo o comportamento legítimo.
2. **Trilha de estudos:** skill com perguntas de diagnóstico, orçamento semanal de horas e critérios de aprendizagem.
3. **Outros cenários:** configuração insegura e infraestrutura com SSH irrestrito e criptografia desabilitada. São JSONs didáticos; nada é implantado.
4. **Saída padronizada:** impacto e probabilidade de 1 a 3; produto classificado como baixa (1–2), média (3–4), alta (6) ou crítica (9). Sem contexto suficiente, o risco fica não determinado. A matriz é própria, não CVSS.
5. **DevSecOps:** workflow para pull requests, push em main e execução manual, com revisão dos arquivos rastreados e das alterações entre commits. O agente faz a revisão semântica; o CI executa regras limitadas e testes, sem chamar um modelo. Veja [o fluxo e suas limitações](docs/devsecops.md).

## Evidências e limites

- [Análise do laboratório](evidence/analise-laboratorio.md): cinco achados, correções e risco contextualizado, usando o modelo comum.
- [Contexto e perguntas](evidence/contexto.md): fatos conhecidos nesta execução e perguntas de demonstração claramente identificadas como roteiro.
- [Saída real dos comandos](evidence/execucao.txt): testes, resultados antes/depois e códigos de saída.
- [Detecção antes](evidence/vulnerable.json) e [depois](evidence/hardened.json): cinco padrões detectados antes e nenhum desses padrões depois.
- [Hashes SHA-256](evidence/sha256.json): identificação dos scripts, skills, testes e exemplos usados na captura.

Para regenerar as saídas e hashes depois de uma alteração:

```powershell
python scripts/capture_evidence.py
```

O scanner retorna **0** sem achados nas regras cobertas, **1** com achados e **2** em erro ou revisão incompleta. Ele não faz análise de fluxo entre funções, inventário de dependências, auditoria de autenticação nem testes de serviços. Os JSONs estáticos mantêm risco não determinado; o relatório do agente adiciona o contexto e a justificativa. “Nenhum achado” não significa segurança comprovada.

Não foram fabricados screenshots nem transcrições de uma sessão independente. Os testes automatizados validam os auxiliares e o laboratório, não comprovam o comportamento futuro de um modelo. O [roteiro de avaliação](docs/avaliacao-manual.md) explica como testar as três skills e capturar prints reais da análise e das perguntas no seu harness. A comparação com um chat genérico é opcional.


Licença: [MIT](LICENSE).
