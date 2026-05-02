# 🏥 Tech Challenge — FIAP Pós 9IADT 2026 — Fase 1
## Sistema inteligente de apoio à triagem de mulheres vítimas de violência

> **Aviso Ético**: Este sistema é um **apoio à decisão clínica**. A avaliação final é sempre responsabilidade do profissional de saúde. Todos os dados são tratados em conformidade com a **LGPD (Lei nº 13.709/2018)**.

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Estrutura do Repositório](#estrutura-do-repositório)
3. [Pré-requisitos](#pré-requisitos)
4. [Instalação do Ambiente](#instalação-do-ambiente)
5. [Preparação dos Dados](#preparação-dos-dados)
6. [Como Usar o Jupyter Notebook](#como-usar-o-jupyter-notebook)
7. [Fluxo do Notebook — Passo a Passo](#fluxo-do-notebook--passo-a-passo)
8. [Artefatos do Modelo](#artefatos-do-modelo)
9. [Modelos Treinados](#modelos-treinados)
10. [Métricas e Avaliação](#métricas-e-avaliação)
11. [Considerações Éticas e Limitações](#considerações-éticas-e-limitações)

---

## Visão Geral

Este projeto desenvolve um **modelo de Machine Learning** capaz de estimar a **probabilidade de violência sexual** em notificações de violência doméstica contra mulheres, com base nos dados do **SINAN** (Sistema de Informação de Agravos de Notificação) do Ministério da Saúde.

O objetivo é auxiliar profissionais de saúde na **triagem clínica**, identificando automaticamente casos com alta probabilidade de violência sexual para priorizar encaminhamentos e exames previstos no protocolo do Ministério da Saúde.

**Variável-alvo**: `VIOL_SEXU` — indica se a notificação contém registro de violência sexual (1 = Sim / 0 = Não).

---

## Estrutura do Repositório

```
.
├── TechChallengeTriagemFeminino.ipynb  # Notebook principal
├── requirements.txt                    # Dependências Python
├── data/                               # Dados de entrada (arquivos .zip com CSVs do SINAN)
│   ├── violencia_BR_2010_a_2018.zip
│   ├── violencia_BR_2019_a_2022.zip
│   ├── violencia_BR_2023_a_2024.zip
│   └── violencia_BR_2025.zip
├── model/                              # Artefatos do modelo treinado (gerados pelo notebook)
│   ├── xgb_viol_sexu.joblib            # Modelo XGBoost treinado
│   ├── imputer.joblib                  # Imputador de valores ausentes (mediana)
│   ├── scaler.joblib                   # StandardScaler (Regressão Logística)
│   └── feature_columns.joblib          # Lista de colunas de entrada esperadas
└── documentos/                         # Documentação de referência
    ├── DIC_DADOS_NET_Violencias_v5.pdf # Dicionário de dados SINAN
    ├── IADT - Fase 1 - Tech challenge A.pdf
    └── relatorio-notebook-machine-learning.pdf
```

---

## Pré-requisitos

- **Python** 3.10 ou superior
- **pip** ou **conda** para gerenciamento de pacotes
- Mínimo de **4 GB de RAM** recomendados (os datasets SINAN podem ser grandes)

---

## Instalação do Ambiente

### 1. Clone o repositório

```bash
git clone https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML.git
cd Fiap_Pos_9AIDT_Fase_01_ML
```

### 2. Crie e ative um ambiente virtual (recomendado)

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

As principais bibliotecas utilizadas são:

| Biblioteca | Versão | Uso |
|---|---|---|
| `numpy` | ≥ 1.26 | Operações numéricas |
| `pandas` | ≥ 2.0 | Manipulação de dados |
| `matplotlib` / `seaborn` | ≥ 3.7 / ≥ 0.13 | Visualizações |
| `scikit-learn` | ≥ 1.3 | Pré-processamento e modelos |
| `xgboost` | ≥ 2.0 | Modelo principal (XGBoost) |
| `shap` | ≥ 0.43 | Explicabilidade do modelo |
| `jupyter` | ≥ 1.0 | Ambiente do notebook |

---

## Preparação dos Dados

Os dados são notificações históricas de violência doméstica contra mulheres, provenientes do **SINAN**, organizados em arquivos `.zip` dentro da pasta `data/`.

**Os arquivos `.zip` já estão incluídos no repositório** — não é necessário baixá-los separadamente. O notebook extrai e carrega os CSVs automaticamente na execução da primeira célula de código.

> O dicionário de variáveis completo está disponível em `documentos/DIC_DADOS_NET_Violencias_v5.pdf`.

---

## Como Usar o Jupyter Notebook

### 1. Inicie o Jupyter

```bash
jupyter notebook
```

Ou, se preferir o JupyterLab:

```bash
jupyter lab
```

### 2. Abra o notebook principal

No navegador, navegue até o arquivo:

```
TechChallengeTriagemFeminino.ipynb
```

### 3. Execute as células em ordem

> ⚠️ **IMPORTANTE**: Execute as células **sempre de cima para baixo**, na ordem em que aparecem. As células seguintes dependem de variáveis criadas nas anteriores.

Há duas formas de executar:

- **Célula por célula**: `Shift + Enter` para executar a célula atual e avançar para a próxima.
- **Todas de uma vez**: Menu `Kernel → Restart & Run All` para reiniciar o kernel e executar todo o notebook do início ao fim (recomendado para garantir reprodutibilidade).

### 4. Acompanhe os resultados

Cada seção gera saídas visuais (gráficos) e textuais (tabelas e métricas) diretamente abaixo das células. Não é necessário nenhuma configuração adicional.

---

## Fluxo do Notebook — Passo a Passo

### 1️⃣ Importar o Dataset

As primeiras células de código definem e executam funções auxiliares que:

1. Localizam todos os arquivos `.zip` na pasta `data/`.
2. Extraem os CSVs contidos nos zips para a mesma pasta.
3. Carregam todos os CSVs com tentativas automáticas de encoding (`latin-1`, `utf-8`, `cp1252`).
4. Concatenam tudo em um único `DataFrame` (`dados_concatenados`).
5. Excluem os CSVs após o carregamento para economizar espaço em disco.

```
Saída esperada:
✅ Extraído: violencia_BR_2025.zip
📥 Carregado: violencia_BR_25.csv (linhas: XXXXX, colunas: XX)
🔗 DataFrames concatenados: X arquivos -> XXXXXX linhas
⏱️  Tempo de carregamento: X.XXs
```

Em seguida, os dados são filtrados para manter apenas **vítimas do sexo feminino** (`CS_SEXO == 'F'`), gerando o DataFrame `dadosFemininos`.

---

### 2️⃣ Análise Exploratória de Dados (EDA)

Esta seção gera visualizações e estatísticas descritivas para entender o dataset:

- **Valores ausentes**: gráfico de barras com as 30 colunas com maior percentual de valores nulos.
- **Distribuição de idades**: histograma com a idade das vítimas (calculada a partir do campo codificado `NU_IDADE_N`).
- **Tipos de violência**: gráfico de prevalência de cada tipo de violência registrada (física, psicológica, sexual, etc.).
- **Perfil do agressor**: distribuição de sexo do agressor e relação vítima–agressor.
- **Repetição da violência**: percentual de casos em que a violência se repetiu.

---

### 3️⃣ Pré-processamento de Dados

Prepara os dados para a modelagem:

- **Seleção de features**: são utilizadas variáveis numéricas (idade), binárias (tipos de violência co-ocorrentes, uso de álcool pelo agressor, automutilação, recorrência) e categóricas (gestação, raça/cor, escolaridade, local de ocorrência, sexo do agressor).
- **Tratamento da variável-alvo** (`VIOL_SEXU`): binarizada em 1 (violência sexual) e 0 (demais), com remoção de registros com valor ignorado (9).
- **Encoding**: valores binários `1→1`, `2→0`, `9→NaN`; variáveis categóricas recebem One-Hot Encoding.
- **Imputação**: valores ausentes são substituídos pela **mediana** (`SimpleImputer`), robusta a outliers.
- **Análise de correlação**: heatmap e gráficos de barras mostrando as features com maior correlação positiva e negativa com o target.

---

### 4️⃣ Modelagem

Configura três modelos de classificação para comparação:

| Modelo | Tipo | Configuração principal |
|---|---|---|
| **Logistic Regression** | Linear | `class_weight='balanced'`, `max_iter=500` |
| **Random Forest** | Ensemble (Bagging) | 200 árvores, `max_depth=8`, `class_weight='balanced'` |
| **XGBoost** | Ensemble (Boosting) | 200 estimadores, `max_depth=6`, `scale_pos_weight` ajustado para desbalanceamento |

A divisão dos dados é **80% treino / 20% teste**, estratificada para preservar a proporção da classe positiva. Os dados de treino e teste são normalizados com `StandardScaler` para uso na Regressão Logística.

---

### 5️⃣ Treinamento e Avaliação dos Modelos

Treina os três modelos e produz:

- **Tabela comparativa de métricas**: Acurácia, Precisão, Recall, F1-Score e ROC-AUC para cada modelo (células em verde = melhor valor por métrica).
- **Matrizes de confusão**: visualização dos acertos e erros de cada modelo no conjunto de teste.
- **Curvas ROC**: comparação da capacidade discriminativa dos três modelos.
- **Feature Importance** (Random Forest): as 15 variáveis com maior importância média (Gini).
- **SHAP** (XGBoost): gráficos de barra e beeswarm mostrando o impacto de cada feature nas previsões do modelo.
- **Relatório de classificação** do melhor modelo (maior F1-Score).

> **Por que priorizar Recall e F1?** Num sistema de triagem clínica, um **falso-negativo** (não identificar uma vítima de violência sexual) tem custo muito mais alto do que um falso-positivo. Por isso, essas métricas têm prioridade sobre a acurácia pura.

---

### 6️⃣ Interpretação Crítica dos Resultados

Célula de texto com análise qualitativa dos resultados, incluindo:

- Justificativa das métricas escolhidas.
- O que os modelos aprenderam (principais features preditivas).
- Como o modelo pode ser usado na prática (alertas automáticos, priorização de casos).
- Limitações éticas (subnotificação, viés, conformidade com LGPD).
- Próximos passos sugeridos.

---

### 7️⃣ Persistência do Modelo

Salva os artefatos necessários para carregar o modelo treinado em uma API (ex.: Flask) sem precisar re-treinar:

```python
joblib.dump(modelo_xgb,      "model/xgb_viol_sexu.joblib")
joblib.dump(imputer,         "model/imputer.joblib")
joblib.dump(scaler,          "model/scaler.joblib")
joblib.dump(feature_columns, "model/feature_columns.joblib")
```

---

## Artefatos do Modelo

Após a execução completa do notebook, a pasta `model/` conterá:

| Arquivo | Conteúdo |
|---|---|
| `xgb_viol_sexu.joblib` | Modelo XGBoost treinado (classificador principal) |
| `imputer.joblib` | `SimpleImputer(strategy='median')` ajustado nos dados de treino |
| `scaler.joblib` | `StandardScaler` ajustado nos dados de treino |
| `feature_columns.joblib` | Lista com os nomes das colunas de entrada, na ordem exata esperada pelo modelo |

Para carregar o modelo em outra aplicação:

```python
import joblib
import pandas as pd

model    = joblib.load("model/xgb_viol_sexu.joblib")
imputer  = joblib.load("model/imputer.joblib")
features = joblib.load("model/feature_columns.joblib")

# X_new deve ser um DataFrame com as mesmas colunas de 'features'
X_imputed = imputer.transform(X_new[features])
proba = model.predict_proba(X_imputed)[:, 1]  # probabilidade de violência sexual
```

---

## Modelos Treinados

| # | Modelo | Tipo | Justificativa |
|---|---|---|---|
| 1 | **Random Forest** | Ensemble (Bagging) | Robusto, estável, boa interpretabilidade via Feature Importance |
| 2 | **XGBoost** | Ensemble (Boosting) | Alta performance em dados tabulares desbalanceados; modelo persistido |
| 3 | **Logistic Regression** | Linear | Interpretável, rápido, serve como baseline de comparação |

---

## Métricas e Avaliação

As métricas calculadas para cada modelo são:

| Métrica | Descrição |
|---|---|
| **Acurácia** | Proporção de acertos no total |
| **Precisão** | Dos casos classificados como positivos, quantos realmente são |
| **Recall** | Dos casos positivos reais, quantos foram identificados *(métrica prioritária)* |
| **F1-Score** | Média harmônica entre Precisão e Recall *(métrica prioritária)* |
| **ROC-AUC** | Área sob a curva ROC; avalia o modelo em todos os limiares de decisão |

---

## Considerações Éticas e Limitações

- O modelo foi treinado em notificações **já registradas**; casos não notificados (subnotificação) introduzem viés.
- Campos preenchidos como "ignorado" (valor 9) reduzem a qualidade das previsões.
- O **profissional de saúde deve sempre ter a palavra final** no diagnóstico e encaminhamento.
- Qualquer uso deve estar em conformidade com a **LGPD (Lei nº 13.709/2018)**.

---

## 📄 Documentos de Referência

- `documentos/DIC_DADOS_NET_Violencias_v5.pdf` — Dicionário de variáveis do SINAN
- `documentos/IADT - Fase 1 - Tech challenge A.pdf` — Enunciado do Tech Challenge
- `documentos/relatorio-notebook-machine-learning.pdf` — Relatório do projeto
