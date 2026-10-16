# Quizz App

Aplicação de quiz simples em [Streamlit](https://streamlit.io), criada para testar o deploy no **Databricks Apps**.

## Estrutura

```
apps/quizz-app/
├── app.py              # Aplicação Streamlit (UI + lógica do quiz)
├── app.yaml            # Comando de execução no Databricks Apps
├── app_diagnostics.py  # Logging de crashes/exceções (stdlib), vindo do template
├── manifest.yaml       # Nome e descrição do app
└── requirements.txt    # Dependências (streamlit)
```

## Como funciona (`app.py`)

### Diagnóstico
O início do arquivo importa `app_diagnostics` e chama `install_diagnostics()` antes de qualquer código da aplicação. Isso envia stack traces de falhas e exceções para os logs do app (`databricks apps logs`). Pode ser desativado com `DATABRICKS_APP_DIAGNOSTICS=0`.

### Perguntas
`QUESTIONS` é uma lista de dicionários:

| Campo     | Descrição                                   |
|-----------|---------------------------------------------|
| `q`       | Texto da pergunta                           |
| `options` | Lista de alternativas                       |
| `answer`  | Índice (base 0) da alternativa correta      |

Para adicionar ou alterar perguntas, edite apenas essa lista.

### Estado (`st.session_state`)

| Chave          | Significado                                      |
|----------------|--------------------------------------------------|
| `idx`          | Índice da pergunta atual                         |
| `score`        | Quantidade de acertos                            |
| `answered`     | Se a pergunta atual já foi respondida            |
| `last_correct` | Se a última resposta estava correta              |
| `results`      | Lista de booleanos (acerto/erro) por pergunta    |

`reset()` inicializa todas essas chaves e é usada no primeiro carregamento e no botão **Reiniciar**.

### Fluxo
1. **Saudação:** mostra o usuário a partir do cabeçalho `X-Forwarded-Preferred-Username`, injetado pelo Databricks Apps. Se ausente (ex.: execução local), mostra apenas "Olá!".
2. **Pergunta:** barra de progresso, `st.radio` com as alternativas (sem seleção inicial) e botão **Responder**, habilitado só após escolher uma opção.
3. **Feedback:** após responder, a alternativa fica bloqueada e aparece "Correto!" ou a resposta certa. O botão **Próxima** (ou **Ver resultado** na última pergunta) avança.
4. **Resultado final:** pontuação e dois gráficos:
   - **Acertos x Erros:** gráfico de rosca (Vega-Lite) com os totais.
   - **Resultado por pergunta:** gráfico de barras (P1…Pn), verde para acerto e vermelho para erro.
   - Botão **Reiniciar** para jogar novamente.

## Executar localmente

```bash
cd apps/quizz-app
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Databricks Apps

1. **Conectar o GitHub:** Settings → Linked accounts → Git integration.
2. **Criar o Git folder:** Workspace → Create → Git folder, com a URL `https://github.com/brenosyperrek/quizz-app.git`. Selecione a branch desejada.
3. **Deploy:** em Compute → Apps, abra o app e clique em **Deploy**. Em *Source code path*, use `/Workspace/Users/<seu-email>/quizz-app/apps/quizz-app`, a pasta que contém o `app.yaml`.
4. **Executar:** com o status *Running*, abra a URL do app.

Para atualizar após novos commits: **Pull** no Git folder e **Deploy** novamente.

Via CLI:

```bash
databricks apps deploy <nome-do-app> --source-code-path /Workspace/Users/<seu-email>/quizz-app/apps/quizz-app
databricks apps logs <nome-do-app>
```

## Dependências
- `streamlit~=1.38.0` (traz `pandas`, usado para montar os dados dos gráficos)
