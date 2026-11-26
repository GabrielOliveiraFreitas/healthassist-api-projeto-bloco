# Agente Autônomo de Triagem — TP4

Agente construído com o **OpenAI Agents SDK** (`Agent` + `Runner` + `@function_tool`).
Código: [`scripts/agent_triagem.py`](../scripts/agent_triagem.py).

## 1. Arquitetura

- **Agent** — `Triagem HealthAssist`, com *system prompt* de atendimento ao paciente:
  usa sempre a ferramenta de classificação, responde de forma acolhedora, **não** dá
  diagnóstico nem prescreve, e escala para humano quando a probabilidade é baixa.
- **@function_tool `classificar_intencao(texto)`** — chama o endpoint `POST /classify`
  da própria HealthAssist API (autenticado por **JWT Bearer**) e devolve a intenção
  prevista + probabilidade + versão do modelo. É a ponte entre o agente e o modelo treinado.
- **Runner.run** — executa o ciclo do agente. A conversa tem **3 turnos**, com o histórico
  repassado entre turnos via `result.to_input_list()` (memória de diálogo).
- **Backend de LLM** — por padrão um **Ollama local** (`qwen2.5:7b`, que suporta *tools*),
  via a API compatível com OpenAI em `http://127.0.0.1:11434/v1`. Assim o agente roda
  **sem chave externa e sem custo**. Para usar a OpenAI, basta `AGENT_OPENAI=1` + `OPENAI_API_KEY`.

```
Paciente → Agent (LLM Ollama) → tool classificar_intencao → POST /classify (JWT) → modelo TF-IDF+LogReg
                     ↑__________________ resposta ao paciente __________________|
```

## 2. Como executar

```bash
# 1. subir a API com o modelo treinado
export SECRET_KEY="<32+ chars>"; export DATABASE_URL="sqlite:///./healthassist.db"
export SEED_ALICE_PASSWORD="<senha>"; python -m scripts.seed
uvicorn app.main:app --port 8710 &
# 2. rodar o agente (Ollama local precisa estar no ar com qwen2.5:7b)
export AGENT_USER=alice AGENT_PASSWORD="<senha>" HEALTHASSIST_URL=http://127.0.0.1:8710
python -m scripts.agent_triagem
```

## 3. Demonstração executada (3 turnos)

Execução real contra `qwen2.5:7b` (Ollama) + API em `127.0.0.1:8710`. O log do servidor
confirmou as chamadas da ferramenta: `POST /auth/token → 200` e várias `POST /classify → 200`
durante a conversa.

> **Turno 1**
> **Paciente:** Oi, fiz uma cirurgia no joelho mês passado. Qual fisioterapia ajuda na recuperação?
> **Agente:** Olá! [...] fisioterapeutas especializados em ortopedia ou na recuperação
> pós-cirúrgica podem ser muito úteis [...]. Vou confirmar com um atendente humano para
> recomendar profissionais específicos da nossa rede [...].

> **Turno 2**
> **Paciente:** E qual especialista eu procuro para acompanhar essa recuperação?
> **Agente:** A intenção detectada foi "Tratamento", e a probabilidade foi alta [...].
> Para acompanhar sua recuperação [...] é recomendável procurar um ortopedista ou um
> fisioterapeuta especializado em reabilitação pós-cirúrgica [...].

> **Turno 3**
> **Paciente:** Entendi. Isso que eu tenho é contagioso para outras pessoas?
> **Agente:** A intenção detectada é "Tratamento", mas a probabilidade é baixa, então vou
> confirmar com um atendente humano [...]. Para te dar a informação mais precisa, preciso
> saber mais sobre o diagnóstico que você recebeu [...].

O agente mantém o contexto entre turnos, usa a ferramenta para obter a intenção do modelo
e aplica a política do *system prompt* (escala para humano quando a probabilidade é baixa,
como no turno 3).

## 4. Observações

- A ferramenta usa o `/classify` **autenticado** (JWT): o agente obtém um token via
  `/auth/token` no início e o reutiliza — mesma postura de segurança da API.
- O modelo local (`qwen2.5:7b`) é suficiente para o *tool calling*; trocar por um modelo
  mais forte (ou pela OpenAI) melhora a fluência das respostas, sem mudar a arquitetura.
