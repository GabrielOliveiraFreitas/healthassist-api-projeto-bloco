Contexto do projeto
Olá! No TP1, você escolheu o dataset, fez a EDA inicial e montou a estrutura da API com autenticação básica. Agora o projeto entra em profundidade.

Neste TP, você vai completar a análise exploratória do dataset — incluindo correlações, testes de hipótese e visualizações sofisticadas — e vai transformar a API FastAPI em uma API de verdade: com todos os controles de segurança do OWASP Top 10 aplicados e auditada por uma ferramenta real (OWASP ZAP). Lembre-se de que, em alguns meses, um colega vai tentar invadir essa API. Quanto mais robusta ela estiver agora, mais interessante vai ser o pentest depois.

Objetivo da entrega
Produzir a análise exploratória completa do dataset e entregar a API FastAPI com controles OWASP Top 10 implementados e auditada por scan passivo ZAP. Este TP corresponde à competência integradora: Implementar análise estatística completa e controles OWASP Top 10 na API FastAPI auditada por ZAP.

Tarefas
Aprofunde a EDA com visualizações avançadas: heatmap de correlação com seaborn, scatter plots relevantes e pelo menos um teste de hipótese formal (t-test ou Mann-Whitney via SciPy) para uma hipótese que você formulou no TP1. Interprete os resultados em linguagem acessível.
Aplique controles OWASP Top 10 na API FastAPI: configure Pydantic com extra='forbid' em todos os modelos de entrada, use SQLModel com queries parametrizadas (sem SQL raw), adicione verificação de ownership (BOLA) nas rotas que retornam recursos por ID.
Configure os headers de segurança HTTP: HSTS, X-Frame-Options, X-Content-Type-Options e Content-Security-Policy via middleware FastAPI. Configure também CORS com allowlist explícita de origens.
Implemente rate limiting no endpoint de autenticação (/auth/token) para prevenir brute force. Documente o limite escolhido e a justificativa técnica.
Execute um scan passivo com OWASP ZAP na API rodando localmente. Exporte o relatório de findings. Para cada finding com severidade Medium ou High, documente: o que foi detectado, por que é um problema e como você corrigiu (ou por que aceitou o risco).
Escreva pelo menos 3 testes pytest cobrindo: (a) tentativa de acesso sem token, (b) tentativa de acesso a recurso de outro usuário, e (c) envio de campo extra no body da request.
Atualize o relatório de EDA como documento estruturado: seções problema, dados, análise, insights principais, limitações e próximos passos (abertura para o modelo de classificação).
Evidências obrigatórias
Notebook de EDA atualizado com heatmap de correlação, scatter plots e pelo menos um teste de hipótese com p-valor interpretado.
Código da API FastAPI atualizado no repositório com Pydantic extra='forbid', SQLModel, verificação de ownership, headers de segurança, CORS e rate limiting — todos funcionando.
Relatório OWASP ZAP exportado (HTML, JSON ou PDF) + documento de findings com severidade, descrição e status (corrigido/aceito com justificativa).
Suite de testes pytest com pelo menos 3 casos de segurança executáveis com pytest tests/ sem erros.
Relatório de EDA como documento separado (.md ou PDF) com as seções definidas na tarefa 7.


**RECLAMAÇÕES DO PROFESSOR!**

Gabriel,

Você apresentou uma implementação consistente da parte de segurança da API prevista no TP2. A estrutura contempla SQLModel, proteção BOLA, Pydantic com rejeição de campos adicionais, headers HTTP de segurança, CORS com allowlist e rate limiting da autenticação. A proteção BOLA foi concebida de maneira adequada ao consultar simultaneamente o identificador do recurso e seu proprietário, retornando 404 tanto para recurso inexistente quanto para recurso pertencente a outro usuário. 

A documentação da auditoria ZAP também apresenta cuidado metodológico. O scan foi realizado por meio de zap-api-scan.py orientado pela especificação OpenAPI, cobrindo quatro rotas. O documento reconhece corretamente que, como o ZAP não recebeu JWT, o scan não constitui evidência de proteção BOLA; essa propriedade precisa ser verificada separadamente pelos testes autenticados. 

O finding identificado pelo ZAP foi tratado adequadamente. A ausência de Cross-Origin-Resource-Policy foi explicada, corrigida com same-origin e submetida a novo scan. O resultado final registrou zero findings Low, Medium ou High. Os quatro alertas restantes foram classificados como informativos e individualmente analisados.

A principal lacuna da entrega está na parte de Ciência de Dados do TP2. O README registra explicitamente que a EDA está sendo conduzida por outro integrante e ainda será adicionada ao repositório. Entretanto, a tarefa avaliada exige como evidências obrigatórias notebook atualizado com heatmap, teste de hipótese e p-valor interpretado, além de relatório estruturado de EDA. O relatório separado também deveria conter as seções determinadas pela atividade.

Assim, mesmo com a parte de segurança substancialmente atendida, a ausência dos artefatos de EDA impede o atendimento das rubricas 1, 2, 3, 11 e 12.

Sugestões para aprofundamento e futuros trabalhos:

Integrar ao repositório o notebook de EDA produzido pelo integrante responsável antes da entrega final do trabalho em equipe.
Incluir no notebook heatmap de correlação explicitamente produzido com seaborn.
Formular e executar pelo menos um teste de hipótese com SciPy, documentando H0/H1, estatística, p-valor, nível de significância e interpretação.
Relacionar explicitamente o teste estatístico às hipóteses formuladas no TP1.
Produzir o relatório separado de EDA com problema, dados, análise, insights e próximos passos.
Relacionar os insights estatísticos ao problema de classificação de sintomas previsto para o TP3.
Manter a separação já adotada entre evidências provenientes do ZAP e evidências de autorização/BOLA obtidas por testes autenticados.
Em futura implantação, validar HSTS em ambiente efetivamente servido por HTTPS e revisar o rate limiting para cenários distribuídos.