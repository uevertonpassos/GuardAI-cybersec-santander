# Revisão antes da produção

O workflow [GuardAI Security](../.github/workflows/security.yml) roda em pull requests, push em main e acionamento manual. Ele verifica a integridade do projeto, executa os testes, inspeciona arquivos rastreados e, em PRs, os arquivos alterados desde o ancestral comum entre a base e o head. Os conteúdos são lidos do commit final; uma modificação posterior no working tree não muda esse resultado.

As ações estão fixadas por SHA, com `contents: read`, sem persistência de credenciais e sem secrets do projeto. Não é usado `pull_request_target`. O workflow não faz deploy nem chama um agente automaticamente. Alterações em dependências, YAML, shell e outros formatos sem regras são listadas para revisão humana.

## Fluxo do desenvolvedor

1. Faça a mudança em uma branch e explique os dados e comportamentos afetados.
2. Use a skill de análise para ler o diff e o contexto afetado. O relatório segue o template comum.
3. Rode validação, testes e `python scripts/security_review.py --tracked`.
4. Se houver dois commits, rode `python scripts/security_review.py --base HEAD~1 --head HEAD`. Para uma branch, substitua a base pela referência da main disponível localmente.
5. Abra o PR e preencha o [template](../.github/pull_request_template.md). Confirme os resultados do CI e revise os formatos sem regras automáticas.
6. Antes de produção, resolva os achados ou documente uma aceitação de risco revisada por uma pessoa responsável. Bloqueie a decisão quando faltar contexto material.

O scanner bloqueia ao detectar qualquer uma das cinco regras, sem inventar uma severidade a partir de dados ausentes. Erros de leitura, sintaxe ou revisão também retornam falha. Uma versão corrigida pode continuar vulnerável a problemas fora da cobertura.

## Exclusões deliberadas

Somente estes três caminhos são excluídos do gate padrão: `lab/vulnerable/app.py`, `lab/vulnerable/config.json` e `lab/vulnerable/infra.json`. São fixtures intencionais, usadas nos testes que exigem a presença dos cinco achados. `--paths` permite revisá-las explicitamente. Novos arquivos na mesma pasta não recebem exceção automática.

Esses exemplos nunca devem ser usados como aplicação de produção. Alterações na lista de exclusões, nos testes ou no workflow exigem revisão humana, pois a própria verificação pode ser enfraquecida por uma alteração maliciosa. Os testes didáticos não substituem análise de todo novo conteúdo dessas fixtures.

## O que depende do GitHub

A configuração está pronta, mas não foi executada no serviço porque não houve push. Após a publicação, configure a proteção da branch para exigir o job `security` do workflow `GuardAI Security` e revisão humana antes do merge. A presença do YAML, sozinha, não impede merges nem implantações. Nenhuma proteção de branch foi configurada remotamente nesta entrega.
