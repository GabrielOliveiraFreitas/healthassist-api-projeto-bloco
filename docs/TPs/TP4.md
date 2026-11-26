Olá, Gabriel.

Chegamos a uma das etapas de preparação! A cada Teste de Performance (TP) você terá a oportunidade de praticar os conhecimentos adquiridos e receber feedbacks relevantes para o seu aprendizado.

Uso de IAs: Sinal Verde 🟢
Neste trabalho, os alunos são incentivados a explorar o uso de ferramentas baseadas em IA para concluir as tarefas. Todas as fontes, incluindo ferramentas de IA, devem ser devidamente citadas. O uso de IA sem a devida citação será considerado má conduta acadêmica e estará sujeito à aplicação do código disciplinar. Observe que os resultados da IA podem ser tendenciosos e imprecisos. É sua responsabilidade garantir que as informações que você usa da IA sejam precisas. Aprender como usar ferramentas baseadas em IA de maneira cuidadosa e estratégica contribui para o desenvolvimento das habilidades, refinamento de seu trabalho e prepara o aluno para sua futura carreira.

Você vai fazer duas coisas em paralelo: construir a inteligência do sistema (o classificador de intenções e o agente autônomo) e atacar a API de um colega com as técnicas que está aprendendo em Análise de Vulnerabilidades e Pentest.

Do lado construtivo: você vai treinar o modelo que classifica a intenção do usuário, integrá-lo à API FastAPI como endpoint, e construir o primeiro agente que usa esse modelo como ferramenta. O sistema começa a ganhar inteligência real.

Do lado ofensivo: você vai executar reconhecimento ativo, testar JWT attacks, lançar fuzzing e injeção de SQL na API do colega. Cada ataque bem-sucedido (ou mal-sucedido) precisa ser documentado com evidências.

Objetivo da entrega
Integrar o classificador de intenções treinado e o agente autônomo à API, e entregar o log parcial do pentest adversarial com ataques JWT, recon e injeção documentados. Este TP corresponde à competência integradora: Integrar o classificador de intenções e o agente autônomo à API com pentest parcial cobrindo recon com Kiterunner e JWT attacks com jwt_tool.

Tarefas
Treine o classificador de intenções com Scikit-learn usando o pipeline definido no TP3 (TF-IDF + LogisticRegression ou SVM). Avalie com matriz de confusão, precision, recall, F1-score por classe e ROC-AUC. Documente o desempenho e compare com uma baseline simples (ex: classificar sempre a classe mais frequente).
Adicione o endpoint POST /classify à API FastAPI: recebe um texto JSON, autentica via JWT, passa pelo modelo treinado e retorna a intenção prevista com a probabilidade. Salve o modelo com joblib ou pickle no repositório.
Configure o GridSearchCV para buscar os melhores hiperparâmetros do classificador (pelo menos 2 parâmetros, pelo menos 3 valores cada). Documente os melhores parâmetros encontrados e o ganho de desempenho.
Construa o agente com OpenAI Agents SDK: crie um Agent com system prompt adequado ao contexto de atendimento ao cliente, implemente a @function_tool que chama o endpoint /classify com o texto do usuário, e use Runner.run para executar o ciclo do agente. Demonstre um exemplo de conversa com pelo menos 3 turnos.
Execute os ataques na API adversária e documente cada um:
JWT attacks: use jwt_tool para executar JWT None Attack (remover assinatura), Algorithm Confusion (RS256→HS256) e crack de segredo HS256 com wordlist. Documente o resultado de cada tentativa: funcionou, por que funcionou (ou por que não).
Reconhecimento ativo: use Kiterunner para descoberta de endpoints de API (é a ferramenta principal — tem wordlists específicas para APIs REST). Complemente com Nmap (varredura de portas) e Gobuster (diretórios). Liste os endpoints descobertos e as tecnologias identificadas.
Autorização quebrada e fuzzing: execute A-B testing entre duas contas de usuários para identificar BOLA (troca de IDs de recursos entre contas) e BFLA (acesso a funções administrativas com token não privilegiado). Use Burp Intruder para enumerar IDs de recursos e verificar IDOR. Execute fuzzing de parâmetros com Wfuzz ou Burp Intruder em busca de endpoints ocultos. Documente cada teste com: método, payload enviado, resposta recebida e avaliação preliminar.
Produza o log parcial de pentest: um documento estruturado com seções para cada tipo de ataque — método usado, payloads enviados, respostas recebidas, e avaliação preliminar sobre vulnerabilidades suspeitas.
Evidências obrigatórias
Notebook de classificação com pipeline completo (TF-IDF + modelo), GridSearchCV, matriz de confusão, métricas por classe e comparação com baseline.
API FastAPI atualizada com endpoint POST /classify funcionando, modelo serializado no repositório, e autenticação JWT no endpoint.
Código do agente (script Python ou notebook) com Agent + Runner + @function_tool funcionando, e demonstração de conversa com 3 turnos documentada.
Log parcial de pentest (arquivo .md na pasta pentest/ do repositório) com seções: JWT attacks (com jwt_tool), reconhecimento ativo (Kiterunner + Nmap), autorização quebrada (BOLA/BFLA/IDOR) e fuzzing — cada um com: método, resultado e evidência (curl output, screenshot de Burp, ou saída de terminal).
Orientações de entrega
Entregue o link do repositório com a pasta pentest/ contendo o log parcial. O agente deve estar funcionando e o notebook de classificação executável. Ataques realizados contra sistemas sem autorização prévia são antiéticos e ilegais — certifique-se de que você tem a autorização do colega adversário por escrito antes de qualquer ataque. O prazo e o formato de entrega serão definidos pelo professor da disciplina.

Assim que terminar, salve seu trabalho em PDF, nomeando o arquivo conforme a regra “nome_sobrenome_PB_TP4.PDF” e poste como resposta a este TP.