# Metodologia de análise — versão 1

## Escopo antes da execução

Registre o objetivo, os arquivos/alvos permitidos, quem controla o ambiente, os dados envolvidos e se o trabalho é leitura estática ou teste ativo. Pergunte apenas o que estiver ausente. Se a autorização de teste não existir, pare a execução ativa; ainda é possível explicar o código fornecido e formular hipóteses.

Para este repositório: todos os dados são fictícios, o banco é SQLite em memória e os JSONs não correspondem a recursos reais. Não há serviço web nem infraestrutura implantada. Uma configuração escrita não prova exposição na Internet.

## Escala ordinal de risco

Esta é uma matriz didática própria, não CVSS, probabilidade estatística nem certificação. Avalie o contexto real separadamente de um cenário hipotético de produção.

| Nota | Impacto | Probabilidade |
| --- | --- | --- |
| 1 | Consequência restrita a dados sintéticos ou ambiente descartável | Exige acesso local ou condições improváveis, sem caminho externo demonstrado |
| 2 | Exposição ou alteração limitada, com recuperação possível | Condições plausíveis, com acesso ou pré-requisito relevante |
| 3 | Dados sensíveis amplamente expostos, privilégio elevado ou serviço essencial indisponível | Caminho acessível e reprodução consistente sob as condições declaradas |

Pontuação = impacto × probabilidade. Severidade: 1–2 = baixa; 3–4 = média; 6 = alta; 9 = crítica. Esses são todos os produtos possíveis de notas inteiras de 1 a 3. Se faltar informação, use `não determinada` nos campos de risco e registre a pergunta pendente, em vez de adivinhar uma nota.

Uma SQL injection reproduzível com dados fictícios tem impacto 1 no laboratório. Se qualquer entrada local reproduz a falha, a probabilidade pode ser 3, resultando em média. Um possível uso em produção deve receber outra avaliação, explicitamente condicional.

## Evidências e decisão

- **Observado:** trecho e localização que sustentam o achado; omita segredos.
- **Reproduzido:** comando autorizado, resultado e condição de teste.
- **Hipótese:** consequência que depende de fatos ainda não verificados.
- **Confiança:** alta quando o comportamento foi reproduzido; média quando só há configuração ou fluxo estático; baixa quando faltam partes do fluxo.
- **Correção:** mudança que atua na causa e teste que demonstra sua eficácia.
- **Conclusão:** o que foi coberto, o que ficou de fora e quem deve decidir sobre implantação.

Não atribua CWE a todo problema por aproximação. Para SQL injection, use CWE-89. Revise autenticação, autorização, manipulação de dados e configuração conforme o escopo, mesmo que os scripts auxiliares não implementem essas verificações.
