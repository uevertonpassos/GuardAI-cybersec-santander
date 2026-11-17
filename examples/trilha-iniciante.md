# Exemplo de trilha — quatro semanas

Premissas deste exemplo: estudante iniciante, noções básicas de computador, quatro horas por semana, Python e Git disponíveis, objetivo de revisar pequenos programas Python. Não é uma personalização baseada em respostas de uma pessoa específica. A skill deve adaptar o plano se nível, tempo ou objetivo mudarem.

| Semana | Objetivo | Conteúdo e tempo | Exercício local | Entrega e critério de aprendizagem |
| --- | --- | --- | --- | --- |
| 1 | Entender o laboratório e limites | 1h terminal/Git; 1h Python/SQLite; 1h prática; 1h revisão | Executar as duas versões com busca normal e ler o AGENTS.md | Explicar como os dados são criados, onde ficam e por que nenhum servidor é necessário |
| 2 | Distinguir instrução e dado | 1h CWE-89/OWASP; 2h comparação e teste; 1h explicação | Reproduzir o caso local e testar um nome com apóstrofo na versão corrigida | Explicar por que a entrada amplia o resultado antes e não depois; mostrar teste legítimo passando |
| 3 | Revisar configuração e infraestrutura | 1h redes/TLS; 1h mínimo privilégio; 1h leitura dos JSONs; 1h relatório | Comparar os JSONs vulneráveis e corrigidos | Identificar quatro valores perigosos, condições de exploração e o que o JSON não prova |
| 4 | Levar a revisão ao desenvolvimento | 1h diff e PR; 1h workflow; 1h regressão; 1h checkpoint | Rodar testes e verificador; revisar uma alteração local usando o template | Entregar relatório com risco justificado e explicar um caso fora da cobertura automática |

Total: 16 horas, quatro por semana. Use [as fontes primárias](../knowledge/referencias.md) e [a metodologia](../knowledge/metodologia.md). Todos os exercícios ficam no laboratório deste repositório; não execute sondagens em alvos públicos.

Checkpoint final: explique, sem copiar, a causa da SQL injection, a razão da correção, a distinção entre risco local e produção e a função da revisão humana no CI. Se algum ponto não estiver claro, repita o exercício correspondente antes de aumentar o escopo. O plano é introdutório, sem promessa de domínio profissional.
