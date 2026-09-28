Chegamos a uma das etapas de preparação! A cada Teste de Performance (TP) você terá a oportunidade de praticar os conhecimentos adquiridos e receber feedbacks relevantes para o seu aprendizado.

Uso de IAs: Sinal Verde 🟢
Neste trabalho, os alunos são incentivados a explorar o uso de ferramentas baseadas em IA para concluir as tarefas. Todas as fontes, incluindo ferramentas de IA, devem ser devidamente citadas. O uso de IA sem a devida citação será considerado má conduta acadêmica e estará sujeito à aplicação do código disciplinar. Observe que os resultados da IA podem ser tendenciosos e imprecisos. É sua responsabilidade garantir que as informações que você usa da IA sejam precisas. Aprender como usar ferramentas baseadas em IA de maneira cuidadosa e estratégica contribui para o desenvolvimento das habilidades, refinamento de seu trabalho e prepara o aluno para sua futura carreira.

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