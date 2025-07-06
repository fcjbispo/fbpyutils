# Plano de Execução: Release v1.6.6

Este plano descreve as etapas para refatorar o sistema de configuração e logging da biblioteca `fbpyutils`, visando maior flexibilidade e desacoplamento.

## 1. Visão Geral e Arquitetura

O objetivo é permitir que a biblioteca seja inicializada de três maneiras distintas, com uma clara precedência:

1.  **Programaticamente (Dicionário):** O aplicativo cliente fornece um dicionário de configuração diretamente.
2.  **Arquivo de Configuração Explícito:** O cliente especifica um caminho para um arquivo `.json` de configuração.
3.  **Padrão (Fallback):** Se nenhuma configuração for fornecida, a biblioteca utiliza o arquivo `fbpyutils/app.json` como padrão.

O diagrama a seguir ilustra o fluxo de inicialização proposto:

:::mermaid
graph TD
    subgraph Client Application
        A[start: Iniciar App] --> B{Usa fbpyutils?};
    end

    subgraph "fbpyutils Initialization"
        C[fbpyutils.setup(config_dict)]
        D[fbpyutils.setup(config_file_path)]
        E[fbpyutils.setup()]
    end

    subgraph "fbpyutils Core"
        F[Env(config)] --> G[Logger.get_from_env(env_instance)]
    end

    B -->|Sim| H{Como configurar?};
    H -->|Dicionário| C;
    H -->|Arquivo .json| D;
    H -->|Padrão| E;

    C --> F;
    D --> F;
    E --> F;

    G --> I[Uso da Biblioteca];

    style F fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:2px
:::

## 2. Etapas de Desenvolvimento

A implementação será dividida nas seguintes etapas:

| Passo | Tarefa | Arquivos Afetados | Descrição |
| :--- | :--- | :--- | :--- |
| 1 | **Atualizar Dependências e Versão** | `pyproject.toml` | Adicionar `pydantic` como dependência explícita e atualizar a versão do projeto para `1.6.6`. |
| 2 | **Refatorar `fbpyutils/__init__.py`** | `fbpyutils/__init__.py` | Remover a função `initialize()` automática. Criar uma nova função `setup(config: Optional[Union[Dict, str]] = None)` que orquestrará a inicialização da `Env` e do `Logger`. |
| 3 | **Ajustar `fbpyutils/env.py`** | `fbpyutils/env.py` | Garantir que a classe `Env` funcione corretamente com a nova função `setup`. A lógica interna parece correta, mas precisa ser validada no novo fluxo. Marcar `load_config` como obsoleto de forma mais visível. |
| 4 | **Ajustar `fbpyutils/logging.py`** | `fbpyutils/logging.py` | Assegurar que `Logger` seja configurado exclusivamente através da instância de `Env` passada pelo `setup`. O método `get_from_env` será o ponto central de configuração. |
| 5 | **Atualizar Testes Unitários** | `tests/` | Criar um novo arquivo de teste, `tests/test_initialization.py`, para validar o novo fluxo de `setup` com dicionário, com caminho de arquivo e com o fallback. Atualizar testes existentes para as classes `Env` e `Logger` se necessário. |
| 6 | **Atualizar Documentação** | `README.md`, `DOC.md` | Documentar o novo processo de inicialização, explicando como os clientes da biblioteca devem chamar `fbpyutils.setup()` para configurar o ambiente. |
| 7 | **Revisão Final e Checkpoint** | N/A | Após a conclusão e aprovação de todas as etapas, executar o prompt `APPLY_CHECKPOINT` para finalizar a release. |
