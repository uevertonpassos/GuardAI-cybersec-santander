# Relatório de análise de segurança

## 1. Contexto e autorização

Análise feita durante a preparação deste projeto, em 17/11/2026. Escopo: os seis arquivos Python/JSON de `lab/vulnerable/` e `lab/hardened/`, com reprodução exclusivamente local. Todos foram criados para esta atividade. A autorização está no pedido de criação e validação do repositório. Dados: Ana Demo e Bruno Demo, em SQLite em memória. Não existe servidor ou infraestrutura implantada.

O risco abaixo é do laboratório real. Uma avaliação de produção permanece não determinada: seria necessário confirmar exposição, dados, autenticação, permissões do banco, TLS intermediário e outros controles. Configurações declarativas não comprovam exploração.

## 2. Resumo

Cinco achados didáticos: um de severidade média e quatro de severidade baixa no contexto local. A versão corrigida não apresenta esses cinco padrões nas verificações realizadas. Não foram encontrados recursos reais expostos nem feito teste de rede.

| ID | Objeto | Impacto | Probabilidade | Pontuação | Severidade local |
| --- | --- | --- | --- | --- | --- |
| SQL001 | Consulta SQL | 1 | 3 | 3 | Média |
| CFG001 | Debug | 1 | 1 | 1 | Baixa |
| CFG002 | Bind/TLS | 1 | 1 | 1 | Baixa |
| INF001 | Origens SSH | 1 | 1 | 1 | Baixa |
| INF002 | Criptografia | 1 | 1 | 1 | Baixa |

## 3. Achados

### SQL001

| Campo | Conteúdo |
| --- | --- |
| ID e título | SQL001 — entrada interpolada na consulta (CWE-89) |
| Localização | lab/vulnerable/app.py, linha 17, função find_user |
| Evidência | A f-string insere name no SQL. A entrada local `' OR '1'='1` retorna as duas linhas sintéticas, embora a busca nominal deva selecionar uma pessoa. |
| Impacto | 1 — ampliação do resultado somente sobre dados fictícios e descartáveis |
| Probabilidade | 3 — qualquer chamada local com essa entrada reproduz o comportamento |
| Pontuação | 1 × 3 = 3 |
| Severidade | Média |
| Confiança | Alta — fluxo lido e comportamento reproduzido |
| Cenário de risco | Em uma aplicação que conectasse essa função a dados reais e entradas externas, poderia haver exposição indevida; esse ambiente não existe no laboratório. |
| Correção | Aplicada em lab/hardened/app.py: marcador `?` e tupla de valores; nenhuma interpolação da entrada no SQL. |
| Validação | Execução dos dois apps e testes de regressão: duas linhas antes, nenhuma depois para a entrada adversarial; busca normal preservada. |

A correção segue a separação entre instrução e valores descrita pela [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), e a classificação corresponde à [CWE-89](https://cwe.mitre.org/data/definitions/89.html).

### CFG001

| Campo | Conteúdo |
| --- | --- |
| ID e título | CFG001 — debug habilitado |
| Localização | lab/vulnerable/config.json, chave debug |
| Evidência | Valor true no JSON; não há aplicação consumindo essa configuração. |
| Impacto | 1 — arquivo didático sem dados reais |
| Probabilidade | 1 — seria necessário implementar e executar um serviço que consumisse o valor |
| Pontuação | 1 × 1 = 1 |
| Severidade | Baixa |
| Confiança | Média — configuração observada; efeito em runtime não testado |
| Cenário de risco | Uma implementação que mostrasse detalhes internos em debug poderia expor informação; não se presume console remoto ou execução de código. |
| Correção | debug false na configuração corrigida. |
| Validação | Regra CFG001 aparece antes e não aparece depois; não houve teste de servidor. |

### CFG002

| Campo | Conteúdo |
| --- | --- |
| ID e título | CFG002 — bind amplo com TLS desabilitado |
| Localização | lab/vulnerable/config.json, chaves bind e tls |
| Evidência | bind 0.0.0.0 e tls false declarados. |
| Impacto | 1 — somente representação local, sem tráfego real |
| Probabilidade | 1 — depende de serviço implantado, roteamento e ausência de proteção intermediária |
| Pontuação | 1 × 1 = 1 |
| Severidade | Baixa |
| Confiança | Média — valores confirmados; exposição não demonstrada |
| Cenário de risco | Se um serviço transmitir dados sensíveis em rede não confiável sem TLS no serviço ou proxy, poderá haver leitura ou alteração do tráfego. |
| Correção | bind 127.0.0.1 e tls true no exemplo corrigido; certificados e terminação TLS exigiriam validação separada em serviço real. |
| Validação | Regra CFG002 presente antes e ausente depois; teste adicional não sinaliza bind público quando TLS está declarado ativo. |

### INF001

| Campo | Conteúdo |
| --- | --- |
| ID e título | INF001 — origem administrativa irrestrita |
| Localização | lab/vulnerable/infra.json, chave ssh_sources |
| Evidência | Origens 0.0.0.0/0 e ::/0. Não há firewall provisionado. |
| Impacto | 1 — exemplo sem host ou credenciais reais |
| Probabilidade | 1 — seria necessário provisionar um serviço acessível; origem ampla não implica autenticação vencida |
| Pontuação | 1 × 1 = 1 |
| Severidade | Baixa |
| Confiança | Média — declaração confirmada; conectividade não testada |
| Cenário de risco | Uma implantação poderia ampliar a superfície de tentativas de acesso administrativo; acesso indevido depende de autenticação e outros controles. |
| Correção | Somente loopback IPv4/IPv6 na versão local corrigida; produção requer definição de rede administrativa apropriada. |
| Validação | Regra INF001 presente antes e ausente depois; teste cobre origem IPv6 irrestrita isoladamente. |

### INF002

| Campo | Conteúdo |
| --- | --- |
| ID e título | INF002 — armazenamento sem criptografia declarada |
| Localização | lab/vulnerable/infra.json, chave storage_encrypted |
| Evidência | Valor false no documento, sem volume real associado. |
| Impacto | 1 — não há dados persistidos nem armazenamento implantado |
| Probabilidade | 1 — depende de implantação e de acesso indevido ao armazenamento ou cópia |
| Pontuação | 1 × 1 = 1 |
| Severidade | Baixa |
| Confiança | Média — valor confirmado; controle do provedor não verificado |
| Cenário de risco | Dados reais em armazenamento acessível poderiam ficar expostos; criptografia não substitui controle de acesso. |
| Correção | storage_encrypted true na representação corrigida; uma implantação precisaria verificar a eficácia e a gestão de chaves. |
| Validação | Regra INF002 aparece antes e não aparece depois; nenhum volume foi criado ou inspecionado. |

## 4. Validação e comparação

As saídas integrais e códigos de saída ficam em [execucao.txt](execucao.txt). Foram executados os apps locais, os 15 testes, o scanner nos dois conjuntos e a validação de integridade. O conjunto vulnerável retorna 1 por conter cinco achados; o corrigido retorna 0. Os JSONs automáticos deixam risco não determinado porque o scanner não decide contexto; este relatório aplica a matriz com o contexto documentado.

Também foi testado um repositório temporário: uma configuração insegura commitada continua sendo sinalizada mesmo quando o working tree é alterado depois para um valor corrigido. Isso verifica que a análise de revisão lê o commit indicado.

## 5. Limitações e próximos passos

O scanner tem cinco regras didáticas e não faz análise interprocedural, dependências, serviços reais, autenticação ou autorização. A análise manual foi limitada aos seis artefatos. A aplicação usa um único fluxo de leitura SQL; não foram demonstradas escrita indevida, execução remota nem comprometimento de servidor.

Decisão: **não bloqueia pelas verificações realizadas** a finalidade educacional, mantendo as fixtures vulneráveis isoladas. **Bloqueia** o uso dessas fixtures como aplicação de produção. A versão corrigida também exige revisão específica antes de qualquer implantação. Publicação e execução do workflow hospedado continuam pendentes por solicitação de não fazer push.
