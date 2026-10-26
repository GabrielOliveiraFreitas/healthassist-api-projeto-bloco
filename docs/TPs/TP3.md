Contexto do projeto
Olá! O TP3 é diferente dos outros — ele marca a virada do projeto.

Você está encerrando o Trimestre 1: a análise estatística está quase completa, a API FastAPI está blindada e auditada. Ao mesmo tempo, você está começando o Trimestre 2: em breve você vai treinar um modelo de classificação e, em paralelo, vai começar a atacar a API de um colega.

Neste TP, o seu trabalho não é adicionar novas funcionalidades ao sistema — é consolidar o que foi construído, documentar as limitações do que foi feito até agora e planejar com precisão o que vem a seguir. O entregável de TP3 é o pivô: o momento em que você demonstra que entendeu o problema analítico profundamente e está pronto para resolvê-lo com machine learning.

Objetivo da entrega
Consolidar o sistema estatístico e a API auditada de T1, documentar as limitações da abordagem analítica atual e produzir o plano técnico para T2. Este TP corresponde à competência integradora: Consolidar o sistema estatístico e a API segura, documentando a transição para a fase preditiva.

Tarefas
Implemente um modelo de regressão linear no dataset (mesmo que a tarefa final seja de classificação — use uma variável numérica derivada, como frequência de palavras, comprimento do texto ou score de sentimento como variável alvo). Calcule R², RMSE e analise os resíduos com residual plot e Q-Q plot. Documente as limitações do modelo.
Complete a cobertura de testes de segurança da API: escreva pelo menos 5 testes pytest cobrindo autenticação, autorização (BOLA), validação de entradas e rate limiting. Verifique que todos passam com pytest tests/ -v.
Integre a suite de testes ao pipeline CI/CD: configure o GitHub Actions para rodar pytest automaticamente a cada push. O workflow deve falhar (e impedir o merge) se algum teste de segurança não passar.
Faça a auditoria final de segurança da API: corrija todos os findings Medium ou High pendentes do ZAP, adicione um endpoint OpenAPI bem documentado (/docs) e verifique que a API está pronta para ser alvo de pentest (rodando sem erros, autenticação funcionando, dados de teste disponíveis).
Formalize a pergunta de classificação: dado um texto de atendimento ao cliente, qual é a intenção do usuário? Documente as classes (intenções) que o modelo vai prever, a distribuição dessas classes no dataset e por que a regressão linear não é adequada para este problema.
Produza o documento de planejamento T2 com: (a) modelo candidato (regressão logística ou SVM), (b) estratégia de feature engineering para texto (TF-IDF, CountVectorizer ou outra), (c) colega adversário identificado e (d) URL ou IP da API adversária que você vai atacar no TP4/TP5.
Evidências obrigatórias
Notebook de regressão com pipeline completo (pré-processamento + LinearRegression + múltipla), métricas (R², RMSE), residual plot, Q-Q plot e seção “limitações e próximos passos”.
Repositório atualizado com suite de testes pytest (pelo menos 5 casos) e workflow GitHub Actions configurado (.github/workflows/security-tests.yml).
Relatório de auditoria final da API: checklist de segurança com status de cada item (resolvido/aceito) e evidência de que a API está pronta como alvo de pentest.
Documento de pergunta de classificação (1–2 páginas) com: definição da tarefa, classes/intenções, distribuição no dataset e justificativa para usar ML supervisionado.
Documento de planejamento T2: modelo candidato, estratégia de features, colega adversário e URL da API alvo -- Não possuimos até o momento um colega adversário para tal.
