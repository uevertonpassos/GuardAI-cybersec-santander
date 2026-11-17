# Executando o GuardAI no harness

Um harness conecta o modelo às instruções, arquivos e ferramentas. Aqui, a especialização está em Markdown; não há API de modelo implementada pelo projeto. O Codex CLI usado para conferir a sintaxe local era a versão 0.169.0 (`codex --help` e `codex --version`). A instalação e autenticação são externas ao repositório e podem exigir conta/plano próprios.

## Codex CLI

Abra o terminal na raiz do projeto e execute `codex -C .`. O `AGENTS.md` fornece instruções do projeto, e as skills ficam na pasta `.agents/skills/`. Leia a [documentação oficial](https://learn.chatgpt.com/docs/build-skills) se sua versão usar outra forma de descoberta.

Envie os prompts abaixo dentro do chat do harness. Não cole `$analise-vulnerabilidades` diretamente como comando PowerShell, porque `$` representa variável no shell.

### Revisão sem antecipar o contexto

```text
Use $analise-vulnerabilidades para analisar lab/vulnerable/app.py.
Antes de qualquer teste, explique que contexto você já conhece pelo
repositório e pergunte apenas o que ainda falta para esta revisão.
```

O laboratório e os testes já estão autorizados pelo AGENTS.md. É correto o agente reconhecer isso sem repetir perguntas. Para demonstrar a falta de contexto, peça uma análise hipotética de uma cópia de código cujo ambiente e proprietário não foram informados; não forneça um alvo real de terceiros.

### Análise e testes autorizados

```text
Use $analise-vulnerabilidades e $testes-seguranca.
Sou responsável por este laboratório; autorizo os testes locais documentados.
Revise lab/vulnerable/app.py, lab/vulnerable/config.json e
lab/vulnerable/infra.json. Compare com lab/hardened/.
Use templates/relatorio.md e diferencie observação de hipótese de produção.
```

### Trilha de estudos

```text
Use $trilha-ciberseguranca. Sou iniciante, tenho 4 horas por semana durante
4 semanas e quero aprender revisão de segurança em Python. Quero práticas
somente neste laboratório e materiais gratuitos. Monte objetivos, entregas,
horas e critérios para eu saber se aprendi.
```

### Revisão orientada ao aprendizado

```text
Estou evoluindo a skill .agents/skills/analise-vulnerabilidades/SKILL.md.
Leia o roteiro e me pergunte, etapa por etapa, o que ficou ambíguo para um
agente. Faça uma pergunta por vez e espere minha resposta. Não quero uma
resposta pronta para copiar: quero entender e construir minha solução.
```

## Outro harness ou DIO Agent do curso

Se o harness do curso carregar Markdown por anexos ou instruções, forneça o [AGENTS.md](../AGENTS.md), a [persona](../persona/guardai.md), a [metodologia](../knowledge/metodologia.md), o [template](../templates/relatorio.md), a skill desejada e os arquivos do caso. Solicite explicitamente a leitura nessa ordem. A configuração exata depende do harness disponibilizado no curso; ela não foi fornecida nem testada aqui.

Sem ferramentas de terminal, o agente pode fazer leitura estática e explicar comandos, mas deve registrar testes como não executados. Não transforme uma previsão de saída em evidência de execução. A autorização para o laboratório não autoriza nenhum endereço de produção.
