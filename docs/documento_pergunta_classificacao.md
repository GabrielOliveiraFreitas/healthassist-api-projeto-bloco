# Pergunta de classificação — HealthAssist API

## 1. Definição da tarefa

Dado o texto de uma pergunta feita por um paciente (coluna `question` do MedPT), qual é a **intenção** dessa pergunta? A resposta é uma entre 7 classes, que estão na coluna `question_type`. Como cada pergunta tem exatamente uma classe, o problema é de **classificação multiclasse** com um único rótulo por texto.

Na API, essa tarefa vai ficar atrás do `POST /predict`: o usuário manda o texto e a API devolve a intenção prevista, que ajuda a direcionar a triagem.

## 2. Classes (intenções)

Usei a amostra de 5.000 linhas. Como cada pergunta aparece várias vezes (uma por resposta de médico), conto também as 1.646 perguntas únicas, porque é isso que o modelo realmente vai ver sem repetição.

| Classe | Linhas | % das linhas | Perguntas únicas | % das únicas |
|---|---|---|---|---|
| Tratamento | 2.187 | 43,7% | 671 | 40,8% |
| Diagnóstico | 1.653 | 33,1% | 604 | 36,7% |
| Escolha de profissionais de saúde | 376 | 7,5% | 114 | 6,9% |
| Epidemiologia | 321 | 6,4% | 118 | 7,2% |
| Estilo de vida saudável | 239 | 4,8% | 62 | 3,8% |
| Outros | 156 | 3,1% | 52 | 3,2% |
| Anatomia e fisiologia | 68 | 1,4% | 25 | 1,5% |

Exemplos reais do dataset:
- **Tratamento:** "Fazer aplicação de ácido hialurônico no ombro para melhorar o movimento da capsulite adesiva funciona?"
- **Escolha de profissionais de saúde:** "Como encontrar o melhor especialista para dupuytren na minha cidade?"
- **Anatomia e fisiologia:** "o que é contratura de dupuytren?"

## 3. Distribuição e pontos de atenção

- **Desbalanceamento forte:** duas classes (Tratamento e Diagnóstico) juntas somam cerca de 77% dos dados, e Anatomia e fisiologia tem só 25 perguntas únicas. Um modelo que chutasse sempre "Tratamento" já acertaria 44% das linhas sem aprender nada, então **acurácia não é uma boa métrica**. Pretendo usar F1 macro e olhar o recall de cada classe.
- **Perguntas repetidas:** a mesma pergunta aparece em várias linhas. Na hora de separar treino e teste, preciso agrupar pela pergunta, senão o mesmo texto cai nos dois lados e o resultado fica inflado (isso já fiz no notebook de regressão).
- **Rótulos que parecem ruidosos:** "O que é artrite gotosa?" está como Diagnóstico, enquanto "o que é contratura de dupuytren?" está como Anatomia e fisiologia, e as duas parecem o mesmo tipo de dúvida. Isso pode limitar o quanto qualquer modelo consegue acertar.

## 4. Por que regressão linear não serve e por que usar ML supervisionado

**Regressão linear não é adequada** porque:
- A saída é uma categoria, não um número. Se eu codificasse as classes como 1 a 7, a regressão trataria "Tratamento" (1) como mais perto de "Diagnóstico" (2) do que de "Outros" (6), uma ordem que não existe.
- A regressão devolve valores contínuos (por exemplo 3,4) que não correspondem a nenhuma classe, e não dá uma probabilidade por classe, que é o que a triagem precisa.
- No TP3, mesmo com um alvo numérico (tamanho da resposta), a regressão deu R² perto de zero (0,003 e 0,006) e resíduos com assimetria positiva e cauda longa, fora do que a regressão linear assume.

**ML supervisionado é adequado** porque já existem rótulos (5.000 exemplos rotulados, 1.646 perguntas únicas), a intenção está no conteúdo das palavras e não no tamanho do texto, e escrever regras manuais por palavra-chave seria frágil com tantas formas diferentes de o paciente escrever. Um classificador aprende esses padrões dos exemplos e dá a probabilidade de cada classe.
