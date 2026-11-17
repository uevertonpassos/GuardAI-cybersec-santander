---
name: testes-seguranca
description: Planeja e executa testes defensivos de regressão em código e laboratórios próprios autorizados, comparando o caso vulnerável à correção sem atingir serviços de terceiros.
---

# Testes de segurança em laboratório

1. Confirme o objetivo, o alvo permitido e a autorização já existente. Os testes locais descritos em `AGENTS.md` estão autorizados. Para outro alvo, obtenha propriedade, limites e técnicas permitidas antes da execução; uma URL não é autorização.
2. Leia o teste ou comando antes de executá-lo. Prefira banco em memória, dados sintéticos e isolamento. Não execute código desconhecido para descobrir o que faz. Interrompa se houver rede externa, dados reais ou efeitos fora do escopo.
3. Defina a expectativa: uma entrada normal deve funcionar nas duas versões; a entrada adversarial deve demonstrar a falha na vulnerável e ser tratada como dado na corrigida. Não basta afirmar que “o comando não deu erro”.
4. Neste projeto execute `python -m unittest discover -s tests -v`. Para inspecionar os casos declarativos, execute `python scripts/security_review.py --paths lab/vulnerable/app.py lab/vulnerable/config.json lab/vulnerable/infra.json`. Esse comando retorna 1 quando encontra regras; não é falha do experimento. A versão `lab/hardened/` deve retornar 0 nas mesmas regras.
5. Registre comando, código de saída, saída real, resultado esperado e observado. Use `templates/relatorio.md` para achados e a matriz de `knowledge/metodologia.md` para risco. Nunca trate o sucesso do scanner como uma auditoria completa.
6. Se a correção falhar, relate o comportamento e a próxima hipótese. Não aumente o escopo automaticamente. Se o teste não puder ser executado, identifique-o como pendente, sem gerar um resultado simulado.

O scanner cobre somente padrões didáticos explícitos: interpolação direta em `execute`, debug habilitado, escuta pública sem TLS declarado, SSH irrestrito e armazenamento sem criptografia declarada. A avaliação semântica e a autorização continuam sendo tarefas do agente.
