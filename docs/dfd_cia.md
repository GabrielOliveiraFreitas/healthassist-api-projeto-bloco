# DFD e Análise CIA — HealthAssist API

## Diagrama de Fluxo de Dados (DFD)

```mermaid
flowchart TB
    subgraph EXT["Zona não confiável (Internet)"]
        USR["Usuário / Paciente<br/>(cliente HTTP)"]
    end

    subgraph API["Zona da aplicação (FastAPI) — trust boundary"]
        HEALTH["GET /health<br/>(sem autenticação)"]
        AUTHR["POST /auth/token<br/>(emite JWT)"]
        PRED["POST /predict<br/>(exige JWT)"]
        JWT["JWT Handler<br/>(cria/valida token)"]
    end

    subgraph FUT["Zona de dados (ainda não implementada) — trust boundary futuro"]
        DB[("Banco de usuários<br/>(hoje: credencial fixa no código)")]
        MODEL[("Modelo de classificação<br/>(dataset EDA do Aluno A)")]
    end

    USR -- "1: requisição sem dados sensíveis" --> HEALTH
    HEALTH -- "2: status da API" --> USR

    USR -- "3: username + password" --> AUTHR
    AUTHR -- "4: valida credencial" --> JWT
    JWT -- "5: gera token assinado (HS256)" --> AUTHR
    AUTHR -- "6: JWT" --> USR

    USR -- "7: sintomas + Bearer token" --> PRED
    PRED -- "8: valida token" --> JWT
    JWT -- "9: username autenticado" --> PRED
    PRED -. "10: (futuro) consulta modelo" .-> MODEL
    PRED -- "11: predição placeholder" --> USR

    AUTHR -. "(futuro) consulta credenciais" .-> DB
```

## Tríade CIA por componente

| Componente | Confidencialidade | Integridade | Disponibilidade |
|---|---|---|---|
| Sintomas do paciente (`PredictRequest.symptoms`) | **Alta** — dado de saúde, não pode vazar nem ser logado em texto puro | Média — não pode ser alterado entre o envio e a classificação | Média — indisponibilidade atrasa a triagem, mas não é uma emergência em si |
| Credenciais (`username`/`password`) | **Alta** — hoje trafegam e são comparadas em texto puro no código (`admin`/`senha123` fixos) | Alta — só o dono da credencial pode gerar um token válido | Baixa — indisponível não gera risco à saúde, só bloqueio de acesso |
| Token JWT | Média — não deve ser interceptável (exige HTTPS em produção) | **Alta** — se for forjado, dá acesso indevido à API | Baixa |
| `SECRET_KEY` (assinatura do JWT) | **Alta** — se vazar, qualquer um forja tokens válidos. Hoje tem valor padrão inseguro (`dev-secret-key-insecure`) caso a variável de ambiente não seja definida | **Alta** | — |
| Predição/recomendação (`PredictResponse`) | Baixa | **Alta** — uma predição adulterada pode induzir a uma conduta médica errada | **Alta** — é a função central do sistema; precisa estar sempre disponível |
| `GET /health` | Baixa — não expõe dado sensível | Baixa | **Alta** — usada por monitoramento para saber se a API está no ar |