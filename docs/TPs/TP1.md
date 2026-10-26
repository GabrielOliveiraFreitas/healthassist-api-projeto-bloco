Contexto do projeto
Olá! Você está começando o Projeto de Bloco: ao final deste bloco, você vai ter construído um sistema de atendimento ao cliente alimentado por inteligência artificial — e depois vai atacar o sistema de um colega para descobrir as falhas de segurança que ele deixou.

Mas antes de atacar, você precisa construir. E, antes de construir um sistema inteligente, você precisa entender os dados. Neste primeiro TP, o seu trabalho é escolher o dataset que vai ser a base de todo o projeto, explorar esses dados com rigor estatístico e montar a estrutura da API que vai servir o sistema ao longo do bloco.

Não se preocupe com o modelo de machine learning nem com o agente agora — isso vem depois. Foque em entender os dados e em fazer a API rodar de forma segura desde o início.

Objetivo da entrega
Produzir a análise exploratória inicial do dataset de atendimento ao cliente e configurar a estrutura base da API FastAPI com autenticação JWT funcional. Este TP corresponde à competência integradora: Definir o domínio do sistema com EDA exploratória e API FastAPI autenticada como base.

Tarefas
Escolha um dataset de atendimento ao cliente com pelo menos 500 amostras e colunas de texto (mensagem ou descrição do chamado) e categoria (intenção ou tipo de atendimento). Documente a fonte, a licença e a razão da escolha.
Realize a EDA inicial no dataset: verifique shape, dtypes, valores ausentes, duplicatas e a distribuição das categorias. Use Pandas para todas as operações e documente cada decisão de limpeza.
Construa histogramas e gráficos de barras para visualizar as distribuições das principais variáveis. Identifique pelo menos 3 hipóteses sobre as "intenções" dos usuários a partir dos padrões observados.
Configure o projeto FastAPI com estrutura modular (rotas, modelos, banco de dados) e implemente autenticação JWT com OAuth2PasswordBearer. A API deve ter pelo menos 3 rotas: GET /health, POST /auth/token e POST /predict (que pode retornar um placeholder por enquanto).
Elabore um DFD básico da API com as entradas, saídas e trust boundaries identificados. Aplique a tríade CIA para cada componente: o que é confidencial, o que precisa de integridade, o que deve estar disponível.
Publique tudo em um repositório git com README contendo instruções para instalar e rodar o projeto localmente.
Evidências obrigatórias
Notebook de EDA (.ipynb ou .py) no repositório com: shape, dtypes, describe(), contagem de valores ausentes, distribuição das categorias e pelo menos 3 visualizações (histograma, gráfico de barras, boxplot ou scatter).
Código da API FastAPI no repositório, executável com uvicorn main:app --reload. Deve responder a /health sem autenticação e retornar 401 para /predict sem token.
DFD (imagem ou .md com diagrama Mermaid) com trust boundaries marcados e análise CIA documentada.
README com: objetivo do projeto, instruções de instalação, instruções de execução e estrutura de pastas.
Documento de escolha do dataset (seção no README ou arquivo separado) com: nome, fonte, link, licença e justificativa.


**RECLAMAÇÕES DO PROFESSOR!**

Olá, Gabriel. Seguem os feedbacks:

Destaques iniciais:

- A documentação demonstra inspeção estrutural e estatística, mas não encontrei evidência clara de execução de df.describe() na entrega.

- Há separação em routes, security, models e configuração. Entretanto, não há camada de banco de dados implementada. O próprio DFD identifica o banco como futuro.

Pontos positivos:

A EDA está bem alinhada ao domínio. Além de cumprir o mínimo quantitativo, vocês também perceberam um problema importante: embora existam 5.000 registros na amostra, há somente 1.646 perguntas distintas, pois uma pergunta pode estar associada a várias respostas médicas. Essa observação demonstra análise dos dados, e não mera execução automática de comandos. Parabéns!

As três hipóteses também são pertinentes. A primeira identifica que Tratamento e Diagnóstico representam quase 77% das perguntas; a segunda reconhece um desbalanceamento de aproximadamente 32:1 entre Tratamento e Anatomia/Fisiologia; e a terceira relaciona comprimento da pergunta com determinadas intenções. Ótimo!

A análise de segurança merece destaque. O DFD identifica claramente as trust boundaries e inclusive distingue componentes ainda não implementados — banco e modelo — dos componentes atuais. A proposta pede exatamente identificação de entradas, saídas, trust boundaries e aplicação da CIA. Muito bom!

A CIA também identifica riscos concretos: sintomas são classificados com confidencialidade alta por constituírem dados de saúde; credenciais recebem C/I altas; SECRET_KEY recebe C/I altas; e a integridade da predição é considerada alta porque uma recomendação adulterada poderia induzir conduta médica incorreta. Excelente!

Principais descontos:

O primeiro é a arquitetura de banco de dados. A atividade exige explicitamente FastAPI modular com “rotas, modelos, banco de dados”. O próprio DFD reconhece que a zona de dados é “ainda não implementada” e que as credenciais atualmente estão fixas no código. Portanto, considero atendimento parcial nesse item.

Também há uma questão de segurança relevante: a CIA registra que as credenciais são atualmente comparadas em texto puro e que existe um valor padrão inseguro dev-secret-key-insecure caso a variável de ambiente não esteja definida. É positivo que vocês tenham identificado os riscos, mas eles continuam sendo fragilidades da implementação! Atentem com relação a isso!

Por fim, pela rubrica estrita que estamos utilizando, não consegui comprovar claramente df.describe(). Há shape, tipos, ausentes, duplicatas e distribuição, mas esse comando específico não está evidenciado na documentação acessível. Por isso aplico apenas um desconto pequeno nesse critério.

Resultado:

A entrega é consistente e cobre praticamente toda a Sprint. Há boa conexão entre EDA, domínio médico, API e modelagem de ameaças. Os descontos concentram-se principalmente na ausência da camada de banco solicitada e em pequenas lacunas de evidência/documentação.

Parecer final:

O trabalho apresenta excelente aderência aos requisitos do TP1. O dataset escolhido é adequado ao domínio médico, possui volume superior ao mínimo exigido e está corretamente documentado quanto à fonte, licença e justificativa. A EDA apresenta distribuição das categorias, análise de duplicidade, três visualizações e três hipóteses pertinentes, destacando corretamente o forte desbalanceamento entre as classes. A API possui estrutura modular, autenticação JWT e os três endpoints obrigatórios. Destacam-se especialmente o DFD e a análise CIA, que identificam adequadamente trust boundaries e classificam individualmente os principais ativos e componentes. Como melhorias, recomenda-se implementar efetivamente a camada de banco de dados prevista na especificação, eliminar credenciais fixas e qualquer fallback inseguro para SECRET_KEY, além de deixar explícita no material de EDA a execução de describe().

Ótimo trabalho!