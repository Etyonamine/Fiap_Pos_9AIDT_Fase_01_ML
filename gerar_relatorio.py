#!/usr/bin/env python3
"""
Gerador do relatório PDF — Tech Challenge - Fase 1
FIAP Pós 9AIDT 2026

Uso:
    python gerar_relatorio.py

Saída:
    documentos/TechChallenge_Fase1_Relatorio_Completo.pdf

Dependências:
    pip install weasyprint
"""

import os, ctypes, sys

# adicionar o diretório de DLLs do MSYS2 antes de qualquer import que carregue bibliotecas nativas
if sys.platform == "win32":
    try:
        os.add_dll_directory(r"C:\msys64\ucrt64\bin")
    except (AttributeError, OSError):
        pass

    for name in ("libpango-1.0-0.dll","libpangocairo-1.0-0.dll","libcairo-2.dll",
                 "libharfbuzz-0.dll","libfreetype-6.dll","libfontconfig-1.dll"):
        try:
            ctypes.WinDLL(os.path.join(r"C:\msys64\ucrt64\bin", name))
        except OSError:
            # ignorar aqui; cffi dará erro detalhado se algo faltar
            pass
# agora importe WeasyPrint (após registrar o diretório de DLLs)
from weasyprint import HTML, CSS
import json

import base64
import io
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ── Configurações ──────────────────────────────────────────────────────────────
NOTEBOOK_PATH  = "TechChallengeTriagemFeminino.ipynb"
OUTPUT_DIR     = "documentos"
OUTPUT_FILE    = os.path.join(OUTPUT_DIR, "TechChallenge_Fase1_Relatorio_Completo.pdf")
DIAGRAM_PATH   = "diagrama_componentes_solucao.png"

# Mapeamento: índice da célula → (número da figura, legenda, texto de interpretação)
CHART_META = {
    12: [
        (
            "Fig. 1",
            "Top 30 colunas com maior percentual de valores ausentes",
            (
                "O gráfico revela que a maioria das colunas do dataset apresenta alto percentual "
                "de valores ausentes ou ignorados. Diversas variáveis excedem 80% de nulos, "
                "demonstrando a necessidade de seleção criteriosa de features. Apenas colunas com "
                "relevância clínica comprovada e menor taxa de ausência foram mantidas para a "
                "modelagem, evitando a introdução de ruído no treinamento dos modelos."
            ),
        )
    ],
    13: [
        (
            "Fig. 2",
            "Distribuição de idades das vítimas (em anos)",
            (
                "A distribuição etária das vítimas confirma a vulnerabilidade de jovens e "
                "adolescentes. A mediana de 25 anos e o primeiro quartil em 16 anos indicam que "
                "a violência doméstica afeta desproporcionalmente mulheres em faixa etária jovem. "
                "A presença expressiva de menores de 18 anos entre as notificações reforça a "
                "necessidade de políticas públicas específicas e protocolos de atendimento "
                "diferenciados para esse grupo vulnerável."
            ),
        )
    ],
    14: [
        (
            "Fig. 3",
            "Prevalência dos tipos de violência registrados",
            (
                "A violência física é o tipo mais notificado (57,1% dos casos), seguida pela "
                "violência psicológica (26,2%) e sexual (15,7%). A co-ocorrência entre diferentes "
                "tipos de violência é um fator relevante para o modelo: casos de violência sexual "
                "frequentemente surgem associados à violência física e psicológica, o que justifica "
                "o uso de variáveis de co-ocorrência como features preditivas."
            ),
        )
    ],
    15: [
        (
            "Fig. 4",
            "Perfil do agressor — sexo e relação com a vítima",
            (
                "A análise do perfil do agressor mostra que o sexo masculino predomina como "
                "perpetrador (aproximadamente 78% dos casos), em consonância com os padrões "
                "epidemiológicos de violência doméstica. Quanto à relação vítima-agressor, o "
                "parceiro íntimo ou cônjuge é o agressor mais frequente, representando mais de "
                "40% dos casos — padrão esperado na violência doméstica contra mulheres e que "
                "orienta a priorização de triagem para esse perfil relacional."
            ),
        )
    ],
    22: [
        (
            "Fig. 5",
            "Correlações negativas das features com VIOL_SEXU (top 10)",
            (
                "As correlações negativas indicam variáveis cujo aumento está associado à menor "
                "probabilidade de violência sexual. A violência física (VIOL_FISIC) e psicológica "
                "(VIOL_PSICO) apresentam correlação negativa moderada com a variável-alvo, "
                "sugerindo que casos de violência sexual ocorrem com perfil distinto dos casos "
                "predominantemente físicos ou psicológicos."
            ),
        ),
        (
            "Fig. 6",
            "Correlações positivas das features com VIOL_SEXU (top 10)",
            (
                "Entre as correlações positivas, características do agressor — como uso de "
                "álcool e sexo masculino — e comportamentos da vítima destacam-se como fatores "
                "associados à maior probabilidade de violência sexual. Esses padrões orientaram "
                "a seleção e ponderação das features utilizadas no treinamento dos modelos "
                "preditivos, priorizando variáveis com maior sinal para o alvo."
            ),
        ),
    ],
    29: [
        (
            "Fig. 7",
            "Matrizes de confusão dos três modelos — conjunto de teste",
            (
                "As matrizes de confusão revelam o comportamento de cada modelo na distinção "
                "entre casos de violência sexual e não-sexual. O XGBoost apresenta o melhor "
                "equilíbrio entre verdadeiros positivos e falsos negativos — fator crítico em "
                "triagem clínica, onde a identificação dos casos positivos (recall) é prioritária "
                "para não deixar vítimas sem atendimento. A Regressão Logística tende a gerar "
                "mais falsos positivos, enquanto o Random Forest mantém boa precisão com menor "
                "recall."
            ),
        )
    ],
    30: [
        (
            "Fig. 8",
            "Curvas ROC — comparativo dos três modelos",
            (
                "As curvas ROC confirmam o excelente desempenho discriminatório de todos os "
                "modelos, com AUC superior a 0,90. O XGBoost lidera com AUC ≈ 0,95, seguido "
                "pelo Random Forest e pela Regressão Logística. Todos os modelos estão muito "
                "acima da linha de referência aleatória (AUC = 0,50), validando a qualidade das "
                "features selecionadas e a efetividade da abordagem de Machine Learning para "
                "esse problema de triagem clínica."
            ),
        )
    ],
    31: [
        (
            "Fig. 9",
            "Feature Importance — Random Forest (Top 15)",
            (
                "O gráfico de importância de features do Random Forest indica que a presença "
                "co-ocorrente de violência psicológica (VIOL_PSICO) e física (VIOL_FISIC) são os "
                "fatores mais preditivos de violência sexual. Características do agressor, como "
                "uso de álcool e sexo, também contribuem de forma significativa. A variável "
                "IDADE_ANOS demonstra relevância moderada, confirmando que a faixa etária é um "
                "fator de risco associado ao tipo de violência."
            ),
        )
    ],
    32: [
        (
            "Fig. 10",
            "SHAP Values — XGBoost (importância média das features)",
            (
                "O gráfico SHAP de barras confirma a relevância das features identificadas pelo "
                "Random Forest com uma perspectiva mais robusta: considera interações entre "
                "variáveis e o impacto médio absoluto de cada feature em todas as predições. "
                "A violência psicológica e características do agressor mantêm destaque, validando "
                "a consistência dos resultados entre os dois métodos de interpretabilidade."
            ),
        ),
        (
            "Fig. 11",
            "SHAP Beeswarm — XGBoost (direção do impacto por amostra)",
            (
                "O diagrama de dispersão SHAP revela a direção do impacto de cada feature. "
                "Valores SHAP positivos (à direita) indicam aumento na probabilidade predita de "
                "violência sexual; valores negativos (à esquerda) indicam redução. A presença "
                "isolada de violência psicológica sem violência física associada é um indicador "
                "positivo relevante, enquanto altos valores de violência física tendem a reduzir "
                "a predição — padrão coerente com os diferentes perfis de violência no dataset."
            ),
        ),
    ],
}

# ── Funções auxiliares ─────────────────────────────────────────────────────────

def load_notebook_images(notebook_path: str) -> dict:
    """Retorna dict {cell_idx: [base64_png, ...]} com as imagens das saídas."""
    with open(notebook_path, encoding="utf-8") as fh:
        nb = json.load(fh)

    images: dict = {}
    for idx, cell in enumerate(nb["cells"]):
        outputs = cell.get("outputs", [])
        cell_imgs = [
            o["data"]["image/png"]
            for o in outputs
            if "data" in o and "image/png" in o.get("data", {})
        ]
        if cell_imgs:
            images[idx] = cell_imgs
    return images


def img_tag(b64: str) -> str:
    """Cria tag <img> a partir de base64 PNG."""
    # WeasyPrint aceita data URI
    return f'<img src="data:image/png;base64,{b64}" class="chart-img" />'


def build_chart_section(cell_idx: int, images: dict) -> str:
    """Gera o HTML de uma seção de gráficos para a célula informada."""
    if cell_idx not in images:
        return ""

    metas = CHART_META.get(cell_idx, [])
    cell_images = images[cell_idx]

    html_parts = []
    for i, b64 in enumerate(cell_images):
        meta = metas[i] if i < len(metas) else (f"Fig. {i + 1}", "Gráfico", "")
        fig_num, caption, interpretation = meta

        html_parts.append(f"""
        <div class="chart-block">
            {img_tag(b64)}
            <p class="chart-caption"><strong>{fig_num}</strong> – {caption}</p>
            {"<p class='chart-interpretation'>" + interpretation + "</p>" if interpretation else ""}
        </div>
        """)

    return "\n".join(html_parts)


def generate_architecture_image() -> str:
    """Gera diagrama de arquitetura dos componentes e retorna como base64 PNG."""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#f8f9fa")

    # ── Definição dos blocos ────────────────────────────────────────────────────
    components = [
        {
            "x": 0.3, "y": 1.0, "w": 2.8, "h": 3.0,
            "color": "#1565c0", "label": "[ WEB ]\n(Frontend)",
            "sub": "JavaScript / TypeScript",
            "repo": "Fiap_Pos_9IADT_Fase_01_WEB",
            "detail": "Interface web para\ntriagem clinica",
        },
        {
            "x": 4.6, "y": 1.0, "w": 2.8, "h": 3.0,
            "color": "#2e7d32", "label": "[ API ]\n(Flask / FastAPI)",
            "sub": "Python - REST",
            "repo": "Fiap_Pos_9AIDT_Fase_01_API",
            "detail": "Endpoints de predicao\ne integracao",
        },
        {
            "x": 8.9, "y": 1.0, "w": 2.8, "h": 3.0,
            "color": "#6a1b9a", "label": "[ ML ]\n(XGBoost)",
            "sub": "Python - Jupyter",
            "repo": "Fiap_Pos_9AIDT_Fase_01_ML",
            "detail": "Modelo treinado\n+ artefatos (.joblib)",
        },
    ]

    for comp in components:
        cx, cy, cw, ch = comp["x"], comp["y"], comp["w"], comp["h"]
        # sombra
        shadow = FancyBboxPatch(
            (cx + 0.07, cy - 0.07), cw, ch,
            boxstyle="round,pad=0.1",
            linewidth=0, facecolor="#cccccc", zorder=1,
        )
        ax.add_patch(shadow)
        # caixa principal
        box = FancyBboxPatch(
            (cx, cy), cw, ch,
            boxstyle="round,pad=0.1",
            linewidth=1.5, edgecolor=comp["color"],
            facecolor="white", zorder=2,
        )
        ax.add_patch(box)
        # cabeçalho colorido
        header = FancyBboxPatch(
            (cx, cy + ch - 1.1), cw, 1.1,
            boxstyle="round,pad=0.1",
            linewidth=0, facecolor=comp["color"], zorder=3,
        )
        ax.add_patch(header)
        # título no cabeçalho
        ax.text(
            cx + cw / 2, cy + ch - 0.55,
            comp["label"],
            ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=4,
        )
        # subtítulo (linguagem)
        ax.text(
            cx + cw / 2, cy + ch - 1.45,
            comp["sub"],
            ha="center", va="center",
            fontsize=8, color=comp["color"], fontstyle="italic", zorder=4,
        )
        # detalhe
        ax.text(
            cx + cw / 2, cy + 0.85,
            comp["detail"],
            ha="center", va="center",
            fontsize=8, color="#444444", zorder=4,
        )
        # nome do repositório
        ax.text(
            cx + cw / 2, cy + 0.22,
            comp["repo"],
            ha="center", va="center",
            fontsize=6.5, color="#888888", zorder=4,
        )

    # ── Setas HTTP entre os blocos ───────────────────────────────────────────────
    arrow_style = dict(
        arrowstyle="<->",
        color="#555555",
        lw=1.8,
        connectionstyle="arc3,rad=0.0",
    )
    ax.annotate(
        "", xy=(4.6, 2.55), xytext=(3.1, 2.55),
        arrowprops=arrow_style, zorder=5,
    )
    ax.text(3.85, 2.80, "HTTP / JSON", ha="center", va="bottom", fontsize=7.5, color="#555")

    ax.annotate(
        "", xy=(8.9, 2.55), xytext=(7.4, 2.55),
        arrowprops=arrow_style, zorder=5,
    )
    ax.text(8.15, 2.80, "joblib / predicao", ha="center", va="bottom", fontsize=7.5, color="#555")

    # ── Título e rodapé ──────────────────────────────────────────────────────────
    ax.text(
        6.0, 4.65,
        "Arquitetura dos Componentes - Tech Challenge Fase 1",
        ha="center", va="center",
        fontsize=12, fontweight="bold", color="#1a237e",
    )
    ax.text(
        6.0, 0.35,
        "Usuario -> WEB -> API -> ML Model  |  Cada camada possui repositorio Git independente",
        ha="center", va="center",
        fontsize=7.5, color="#888888",
    )

    plt.tight_layout(pad=0.3)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


# ── HTML do relatório ──────────────────────────────────────────────────────────

CSS_STYLE = """
@page {
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @bottom-center {
        content: "Documento gerado automaticamente · Todos os dados tratados conforme LGPD (Lei nº 13.709/2018)";
        font-size: 7pt;
        color: #888;
    }
    @bottom-right {
        content: "Pág. " counter(page);
        font-size: 8pt;
        color: #555;
    }
    @top-center {
        content: "FIAP Pós 9AIDT 2026 – Fase 1 | Tech Challenge - Fase 1 | Sistema de Triagem";
        font-size: 8pt;
        color: #555;
        border-bottom: 0.5pt solid #ccc;
        padding-bottom: 4pt;
    }
}

body {
    font-family: "DejaVu Sans", Arial, sans-serif;
    font-size: 10pt;
    color: #222;
    line-height: 1.5;
}

/* Capa */
.cover {
    page-break-after: always;
    text-align: center;
    padding-top: 60pt;
}
.cover-title {
    font-size: 28pt;
    font-weight: bold;
    color: #1a237e;
    margin-bottom: 8pt;
}
.cover-subtitle {
    font-size: 14pt;
    color: #37474f;
    margin-bottom: 6pt;
}
.cover-meta {
    font-size: 10pt;
    color: #607d8b;
    margin-top: 20pt;
}
.cover-warning {
    margin-top: 40pt;
    font-size: 8.5pt;
    color: #555;
    border: 1pt solid #bbb;
    padding: 8pt;
    background: #f9f9f9;
    text-align: left;
}

/* Seções */
h1 {
    font-size: 16pt;
    color: #1a237e;
    border-bottom: 1.5pt solid #1a237e;
    padding-bottom: 4pt;
    margin-top: 18pt;
    page-break-after: avoid;
}
h2 {
    font-size: 12pt;
    color: #283593;
    margin-top: 14pt;
    page-break-after: avoid;
}
h3 {
    font-size: 10.5pt;
    color: #37474f;
    margin-top: 10pt;
    page-break-after: avoid;
}

p { margin: 6pt 0; }

ul { margin: 4pt 0 8pt 18pt; }
li { margin-bottom: 3pt; }

/* Tabelas */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
    margin: 8pt 0;
}
th {
    background: #1a237e;
    color: #fff;
    padding: 5pt 6pt;
    text-align: left;
}
td {
    padding: 4pt 6pt;
    border-bottom: 0.5pt solid #ddd;
}
tr:nth-child(even) td { background: #f5f5f5; }

/* Código */
pre, code {
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 7.5pt;
    background: #f4f4f4;
    border: 0.5pt solid #ddd;
    border-radius: 3pt;
}
pre {
    padding: 6pt 8pt;
    white-space: pre-wrap;
    word-break: break-all;
}
code { padding: 1pt 3pt; }

/* Gráficos */
.chart-block {
    margin: 14pt 0 20pt 0;
    page-break-inside: avoid;
}
.chart-img {
    max-width: 100%;
    display: block;
    margin: 0 auto;
    border: 0.5pt solid #ddd;
}
.chart-caption {
    font-size: 8.5pt;
    color: #555;
    text-align: center;
    margin-top: 4pt;
    font-style: italic;
}
.chart-interpretation {
    font-size: 9pt;
    color: #333;
    background: #f0f4ff;
    border-left: 3pt solid #3949ab;
    padding: 7pt 10pt;
    margin-top: 6pt;
    border-radius: 0 3pt 3pt 0;
}

/* Caixa de aviso */
.warning-box {
    background: #fff3e0;
    border-left: 4pt solid #e65100;
    padding: 8pt 12pt;
    font-size: 8.5pt;
    color: #444;
    margin: 12pt 0;
    border-radius: 0 3pt 3pt 0;
}

/* Diagrama de arquitetura */
.arch-diagram {
    text-align: center;
    margin: 16pt 0 6pt 0;
    page-break-inside: avoid;
}
.arch-diagram img {
    max-width: 100%;
    border: 0.5pt solid #ddd;
}

/* TOC */
.toc-item { margin: 3pt 0; font-size: 9.5pt; }
"""


def build_html(images: dict, generated_at: str) -> str:
    """Monta o HTML completo do relatório."""

    # ── Seções de gráficos ──────────────────────────────────────────────────────
    sec_eda_figs = (
        build_chart_section(12, images)   # Fig 1 – missing values
        + build_chart_section(13, images)  # Fig 2 – ages
        + build_chart_section(14, images)  # Fig 3 – violence types
        + build_chart_section(15, images)  # Fig 4 – aggressor
    )
    sec_corr_figs = (
        build_chart_section(22, images)   # Fig 5/6 – correlation
    )
    sec_eval_figs = (
        build_chart_section(29, images)   # Fig 7 – confusion matrices
        + build_chart_section(30, images)  # Fig 8 – ROC
        + build_chart_section(31, images)  # Fig 9 – feature importance RF
        + build_chart_section(32, images)  # Fig 10/11 – SHAP
    )

    arch_section = ""
    if arch_b64:
        arch_section = f"""
<!-- ══ 10. ARQUITETURA ═══════════════════════════════════════════════════════ -->
<h1>10. Arquitetura dos Componentes</h1>
<p>
  A solução é composta por três camadas independentes que se comunicam via HTTP/JSON.
  Cada camada possui seu próprio repositório Git e pode ser implantada separadamente.
</p>
<div class="arch-diagram">
  <img src="data:image/png;base64,{arch_b64}" alt="Diagrama de arquitetura dos componentes" />
  <p class="chart-caption"><strong>Fig. Arq.</strong> – Diagrama de arquitetura: WEB → API → Modelo ML</p>
</div>
<table>
  <tr>
    <th>Camada</th>
    <th>Tecnologia</th>
    <th>Responsabilidade</th>
    <th>Repositório</th>
  </tr>
  <tr>
    <td><strong>WEB</strong> (Frontend)</td>
    <td>JavaScript / TypeScript</td>
    <td>Interface de triagem para profissionais de saúde</td>
    <td><a href="https://github.com/Etyonamine/Fiap_Pos_9IADT_Fase_01_WEB">Fiap_Pos_9IADT_Fase_01_WEB</a></td>
  </tr>
  <tr>
    <td><strong>API</strong> (Backend)</td>
    <td>Python · Flask / FastAPI</td>
    <td>Endpoints REST que recebem dados e retornam predições</td>
    <td><a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_API">Fiap_Pos_9AIDT_Fase_01_API</a></td>
  </tr>
  <tr>
    <td><strong>ML</strong> (Modelo)</td>
    <td>Python · XGBoost / scikit-learn</td>
    <td>Modelo treinado, imputer e scaler persistidos via joblib</td>
    <td><a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML">Fiap_Pos_9AIDT_Fase_01_ML</a></td>
  </tr>
</table>
"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<style>{CSS_STYLE}</style>
</head>
<body>

<!-- ══ CAPA ═════════════════════════════════════════════════════════════════ -->
<div class="cover">
  <p style="font-size:36pt; margin:0;">🏥</p>
  <p class="cover-title">Tech Challenge - Fase 1</p>
  <p class="cover-subtitle">Sistema Inteligente de Apoio à Triagem de<br/>Mulheres Vítimas de Violência</p>
  <p class="cover-meta">
    FIAP Pós-Graduação · Turma 9AIDT · 2026<br/>
    Gerado em: {generated_at}
  </p>
  <table style="margin-top:20pt; font-size:7pt;text-align:left;">
    <tr>
      <th colspan = "2">Referência dos DataSet</th>
    </tr>
    <tr>
      <th>Item</th>
      <th>Descrição</th>
    </tr>
    <tr>
      <td>
        Dicionário de dados do dataset
      </td>
      <td>
        SINAN (Sistema de Informação de Agravos de Notificação) – Ministério da Saúde do Brasil<br/>
        Dicionário de variáveis: <code>documentos/DIC_DADOS_NET_Violencias_v5.pdf</code>
      </td>
    </tr>
    <tr>
      <td>
        Link de download do dataset
      </td>
      <td>
        <a href="https://tabnet.datasus.gov.br/cgi/deftohtm.exe?sinannet/cnv/violebr.def">Link DATASUS - TABNET - VIOLÊNCIA INTERPESSOAL/AUTOPROVOCADA - Brasil</a>
      </td>
    </tr>
  </table>
  <table style="margin-top:20pt; font-size:7pt;text-align:left;">
    <tr>
      <th>Video - apresentação do Tech Challenge</th>      
    </tr>
    <tr>
      <td>
        <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Video - apresentação do Tech Challenge</a>
      </td>
    </tr>
  </table>
  <table style="margin-top:20pt; font-size:7pt;text-align:left;">
    <tr>
      <th>Repositório</th>
      <th>URL</th>
      <th>Descrição</th>
    </tr>
    <tr>
      <td>ML (Machine Learning)</td>
      <td><a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML">https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML</a></td>
      <td>Notebook, datasets, modelos treinados</td>
    </tr>
    <tr>
      <td>API (Flask/FastAPI)</td>
      <td><a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_API">https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_API</a></td>
      <td>API REST para servir o modelo</td>
    </tr>
    <tr>
      <td>WEB (Frontend)</td>
      <td><a href="https://github.com/Etyonamine/Fiap_Pos_9IADT_Fase_01_WEB">https://github.com/Etyonamine/Fiap_Pos_9IADT_Fase_01_WEB</a></td>
      <td>Interface web para triagem</td>
    </tr>
  </table>

  <div class="cover-warning">
    ⚠️ <strong>Aviso Ético:</strong> Este sistema é um apoio à decisão clínica. A avaliação final
    é sempre responsabilidade do profissional de saúde. Todos os dados são tratados em conformidade
    com a <strong>LGPD (Lei nº 13.709/2018)</strong>.
  </div>
</div>

<!-- ══ 1. VISÃO GERAL ════════════════════════════════════════════════════════ -->
<h1>1. Visão Geral do Projeto</h1>
<p>
  Este projeto desenvolve um modelo de <strong>Machine Learning</strong> capaz de estimar a
  probabilidade de <strong>violência sexual</strong> em notificações de violência doméstica contra
  mulheres, com base nos dados do <strong>SINAN</strong> (Sistema de Informação de Agravos de
  Notificação) do Ministério da Saúde.
</p>
<p>
  O objetivo é auxiliar profissionais de saúde na <strong>triagem clínica</strong>, identificando
  automaticamente casos com alta probabilidade de violência sexual para priorizar encaminhamentos
  e exames previstos no protocolo do Ministério da Saúde.
</p>
<p>
  <strong>Variável-alvo:</strong> <code>VIOL_SEXU</code> — indica se a notificação contém registro
  de violência sexual (1 = Sim / 0 = Não).
</p>

<!-- ══ 2. LINKS ══════════════════════════════════════════════════════════════ -->
<h1>2. Links dos Repositórios Git</h1>
<table>
  <tr>
    <th>Componente</th>
    <th>Repositório Git</th>
    <th>Linguagem / Framework</th>
  </tr>
  <tr>
    <td>Machine Learning</td>
    <td><a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML">Clique aqui para baixar</a></td>
    <td>Python · Jupyter / XGBoost</td>
  </tr>
  <tr>
    <td>API REST</td>
    <td><a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_API">Clique aqui para baixar</a></td>
    <td>Python · Flask / FastAPI</td>
  </tr>
  <tr>
    <td>Frontend Web</td>
    <td><a href="https://github.com/Etyonamine/Fiap_Pos_9IADT_Fase_01_WEB">Clique aqui para baixar</a></td>
    <td>JavaScript / TypeScript</td>
  </tr>
</table>

<!-- ══ 3. ESTRUTURA ══════════════════════════════════════════════════════════ -->
<h1>3. Código-Fonte e Estrutura do Repositório (ML)</h1>
<p>O repositório de Machine Learning contém os seguintes artefatos principais:</p>
<pre>
.
├── TechChallengeTriagemFeminino.ipynb   ← Notebook principal (código completo)
├── gerar_relatorio.py                   ← Script gerador deste relatório PDF
├── requirements.txt                     ← Dependências Python
├── data/                                ← Datasets SINAN (arquivos .zip)
│   ├── violencia_BR_2010_a_2018.zip
│   ├── violencia_BR_2019_a_2022.zip
│   ├── violencia_BR_2023_a_2024.zip
│   └── violencia_BR_2025.zip
├── model/                               ← Artefatos do modelo treinado
│   ├── xgb_viol_sexu.joblib             ← Modelo XGBoost
│   ├── imputer.joblib                   ← SimpleImputer (mediana)
│   ├── scaler.joblib                    ← StandardScaler
│   └── feature_columns.joblib           ← Lista de colunas de entrada
└── documentos/                          ← Documentação de referência
    ├── DIC_DADOS_NET_Violencias_v5.pdf  ← Dicionário SINAN
    └── TechChallenge_Fase1_Relatorio_Completo.pdf  ← Este relatório
</pre>

<!-- ══ 4. README ══════════════════════════════════════════════════════════════ -->
<h1>4. README — Instruções de Execução</h1>

<h2>4.1 Pré-requisitos</h2>
<ul>
  <li>Python 3.10 ou superior</li>
  <li><code>pip</code> ou <code>conda</code> para gerenciamento de pacotes</li>
  <li>Mínimo de 4 GB de RAM recomendados (datasets SINAN podem ser grandes)</li>
</ul>

<h2>4.2 Instalação do Ambiente</h2>
<pre>
# 1. Clone o repositório
git clone https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML.git
cd Fiap_Pos_9AIDT_Fase_01_ML

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\\Scripts\\activate   # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o Jupyter
jupyter notebook
</pre>

<h2>4.3 Dependências Principais</h2>
<table>
  <tr><th>Biblioteca</th><th>Versão</th><th>Uso</th></tr>
  <tr><td>numpy</td><td>≥ 1.26</td><td>Operações numéricas</td></tr>
  <tr><td>pandas</td><td>≥ 2.0</td><td>Manipulação de dados</td></tr>
  <tr><td>matplotlib</td><td>≥ 3.7</td><td>Visualizações</td></tr>
  <tr><td>seaborn</td><td>≥ 0.13</td><td>Visualizações estatísticas</td></tr>
  <tr><td>scikit-learn</td><td>≥ 1.3</td><td>Pré-processamento e modelos</td></tr>
  <tr><td>xgboost</td><td>≥ 2.0</td><td>Modelo principal</td></tr>
  <tr><td>shap</td><td>≥ 0.43</td><td>Explicabilidade</td></tr>
  <tr><td>weasyprint</td><td>≥ 60</td><td>Geração do relatório PDF</td></tr>
</table>

<h2>4.4 Execução do Notebook</h2>
<p>
  Após instalar as dependências, abra o arquivo
  <code>TechChallengeTriagemFeminino.ipynb</code> no Jupyter. Execute as células sempre
  de cima para baixo — cada célula depende das anteriores. Use
  <em>Kernel → Restart &amp; Run All</em> para reprodutibilidade completa.
</p>
<p>
  Para regenerar este relatório PDF, execute após o notebook:
</p>
<pre>python gerar_relatorio.py</pre>

<!-- ══ 5. DATASET ═════════════════════════════════════════════════════════════ -->
<h1>5. Dataset</h1>

<h2>5.1 Fonte dos Dados</h2>
<p>
  Os dados são notificações históricas de violência doméstica contra mulheres, provenientes
  do <strong>SINAN</strong> (Sistema de Informação de Agravos de Notificação) do Ministério
  da Saúde do Brasil. Os arquivos <code>.zip</code> já estão incluídos no repositório — não
  é necessário baixá-los separadamente.
</p>

<h2>5.2 Arquivos do Dataset</h2>
<table>
  <tr><th>Arquivo ZIP</th><th>Período</th><th>Observação</th></tr>
  <tr><td>violencia_BR_2010_a_2018.zip</td><td>2010–2018</td><td>73.794 a 350.354 linhas/ano</td></tr>
  <tr><td>violencia_BR_2019_a_2022.zip</td><td>2019–2022</td><td>405.497+ linhas/ano</td></tr>
  <tr><td>violencia_BR_2023_a_2024.zip</td><td>2023–2024</td><td>Dados recentes</td></tr>
  <tr><td>violencia_BR_2025.zip</td><td>2025</td><td>Dados mais recentes (treino)</td></tr>
</table>

<h2>5.3 Características Gerais</h2>
<p>
  Após carregar e filtrar apenas vítimas do sexo feminino, o dataset consolidado possui
  <strong>2.905.198 linhas × 355 colunas</strong>. As primeiras colunas contêm informações
  de identificação, datas e localização; as demais codificam tipos de violência, características
  da vítima e do agressor.
</p>

<h2>5.4 Link para Download</h2>
<p>
  Os arquivos ZIP estão disponíveis diretamente no repositório GitHub:<br/>
  <code>https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML/tree/main/data</code>
</p>
<p>
  O dicionário de variáveis completo está disponível em
  <code>documentos/DIC_DADOS_NET_Violencias_v5.pdf</code>.
</p>

<!-- ══ 6. RELATÓRIO TÉCNICO ══════════════════════════════════════════════════ -->
<h1>6. Relatório Técnico</h1>

<h2>6.1 Análise Exploratória de Dados (EDA)</h2>
<p>A análise exploratória revelou as seguintes características do dataset SINAN:</p>
<ul>
  <li><strong>Volume:</strong> 2.905.198 registros femininos × 355 colunas — dataset de grande
      porte com alta dimensionalidade.</li>
  <li><strong>Valores ausentes:</strong> 243 colunas com mais de 80% de valores nulos; apenas 7
      colunas sem nenhum valor ausente. Isso indicou necessidade de seleção criteriosa de features
      e estratégia robusta de imputação.</li>
  <li><strong>Distribuição de idades:</strong> média de 27,9 anos (DP 16,9); Q25 = 16 anos,
      mediana = 25 anos. Alta proporção de vítimas jovens e adolescentes.</li>
  <li><strong>Tipos de violência (% de casos com Sim):</strong> Física 57,1% · Psicológica 26,2%
      · Sexual 15,7% · Negligência 8,5% · Outras 16,9%.</li>
  <li><strong>Variável-alvo (VIOL_SEXU):</strong> dataset desbalanceado — 16,6% positivos
      (violência sexual) vs. 83,4% negativos. Exigiu estratégias de balanceamento no treinamento.</li>
  <li><strong>Perfil do agressor:</strong> uso de álcool confirmado em 24,1% dos casos, ignorado
      em 31,3%. Violência recorrente em 41,1% dos casos.</li>
  <li><strong>Local de ocorrência:</strong> Residência 69,3%, Via pública 10,6%.</li>
</ul>

<h2>Visualizações da Análise Exploratória</h2>
{sec_eda_figs}

<h2>6.2 Estratégias de Pré-processamento</h2>

<h3>Seleção de Features</h3>
<p>
  Foram selecionadas variáveis com menor taxa de nulos e maior relevância clínica: idade
  (numérica), tipos de violência co-ocorrentes (VIOL_FISIC, VIOL_PSICO, VIOL_TORT, etc.),
  uso de álcool pelo agressor, automutilação, recorrência, gestação, raça/cor, escolaridade,
  local de ocorrência e sexo do agressor.
</p>

<h3>Tratamento da Variável-alvo</h3>
<p>
  <code>VIOL_SEXU</code> binarizada: 1 → violência sexual; 2 → sem violência sexual → 0.
  Registros com valor 9 (ignorado) foram removidos para não introduzir ruído.
</p>

<h3>Encoding de Variáveis Binárias</h3>
<p>
  Variáveis binárias seguiram o padrão SINAN: 1 → 1, 2 → 0, 9 → NaN (tratado na etapa de
  imputação). Variáveis categóricas (gestação, raça, escolaridade, local e sexo do agressor)
  receberam <em>One-Hot Encoding</em>.
</p>

<h3>Imputação de Valores Ausentes</h3>
<p>
  Aplicado <code>SimpleImputer</code> com <code>strategy='median'</code> — robusto a outliers
  e adequado para variáveis ordinais do SINAN. Após imputação: 0 valores ausentes em 46 features.
</p>

<h3>Divisão Treino/Teste</h3>
<p>
  Divisão estratificada 80/20: 2.206.872 amostras de treino e 551.719 de teste, preservando
  a proporção de 16,6% de positivos em ambos os conjuntos.
</p>

<h3>Normalização</h3>
<p>
  <code>StandardScaler</code> aplicado nos dados de treino e transformado nos de teste,
  necessário apenas para a Regressão Logística.
</p>

<h2>Visualizações de Correlação</h2>
{sec_corr_figs}

<h2>6.3 Modelos Utilizados e Justificativa</h2>
<p>
  Foram treinados e comparados três modelos de classificação, escolhidos para cobrir diferentes
  abordagens (linear, ensemble por bagging e ensemble por boosting):
</p>
<table>
  <tr>
    <th>Modelo</th>
    <th>Tipo</th>
    <th>Configuração Principal</th>
    <th>Justificativa</th>
  </tr>
  <tr>
    <td>Logistic Regression</td>
    <td>Linear</td>
    <td><code>class_weight='balanced'</code>, <code>max_iter=500</code></td>
    <td>Interpretável, rápido, baseline de comparação</td>
  </tr>
  <tr>
    <td>Random Forest</td>
    <td>Ensemble (Bagging)</td>
    <td>200 árvores, <code>max_depth=8</code>, <code>class_weight='balanced'</code></td>
    <td>Robusto, estável, Feature Importance interpretável</td>
  </tr>
  <tr>
    <td>XGBoost</td>
    <td>Ensemble (Boosting)</td>
    <td>200 estimadores, <code>max_depth=6</code>, <code>scale_pos_weight</code> ajustado</td>
    <td>Estado da arte em dados tabulares desbalanceados</td>
  </tr>
</table>

<h2>6.4 Resultados e Interpretação dos Dados</h2>

<h3>Métricas Comparativas dos Modelos</h3>
<p>
  Os três modelos foram avaliados no conjunto de teste (551.719 amostras) com as seguintes métricas:
</p>
<table>
  <tr>
    <th>Modelo</th>
    <th>Acurácia</th>
    <th>Precisão*</th>
    <th>Recall*</th>
    <th>F1-Score*</th>
    <th>ROC-AUC</th>
  </tr>
  <tr>
    <td>Logistic Regression</td>
    <td>~88%</td>
    <td>—</td><td>—</td><td>—</td>
    <td>~0.95</td>
  </tr>
  <tr>
    <td>Random Forest</td>
    <td>~91%</td>
    <td>—</td><td>—</td><td>—</td>
    <td>~0.95</td>
  </tr>
  <tr>
    <td><strong>XGBoost</strong></td>
    <td><strong>92%</strong></td>
    <td><strong>72%</strong></td>
    <td><strong>88%</strong></td>
    <td><strong>79%</strong></td>
    <td><strong>~0.95</strong></td>
  </tr>
</table>
<p><small>* Métricas para a classe positiva (Sexual). XGBoost é o modelo vencedor por F1-Score e Recall.</small></p>

<h3>Relatório Completo do Modelo Vencedor (XGBoost)</h3>
<pre>
              precision    recall  f1-score   support

  Não sexual       0.97      0.93      0.95    459,969
      Sexual       0.72      0.88      0.79     91,750

    accuracy                           0.92    551,719
   macro avg       0.85      0.91      0.87    551,719
weighted avg       0.93      0.92      0.92    551,719
</pre>

<h2>Visualizações de Avaliação dos Modelos</h2>
{sec_eval_figs}

<!-- ══ 7. INTERPRETAÇÃO CRÍTICA ════════════════════════════════════════════════ -->
<h1>7. Interpretação Crítica dos Resultados</h1>

<h2>Métricas Escolhidas e Justificativa</h2>
<p>
  Num sistema de triagem médica, <strong>errar para o lado da segurança</strong> é preferível.
  Um <strong>falso-negativo</strong> (não identificar uma vítima de violência sexual) tem custo
  muito mais alto do que um falso-positivo (acionar protocolos desnecessariamente). Por isso
  priorizei o <strong>Recall</strong> e <strong>F1-score</strong> em detrimento da acurácia pura.
  O <strong>ROC-AUC</strong> complementa avaliando o modelo em todos os limiares de decisão
  possíveis.
</p>

<h2>O Que os Modelos Aprenderam</h2>
<p>
  As features com maior impacto identificadas pelo SHAP/Feature Importance revelam que
  <strong>tipo de violência co-ocorrente</strong> (física, psicológica) e <strong>características
  do agressor</strong> (sexo, uso de álcool) são os principais sinais preditivos, em consonância
  com a literatura sobre violência doméstica.
</p>

<h2>Pode Ser Usado na Prática?</h2>
<p>O modelo <strong>pode apoiar</strong> a triagem clínica, funcionando como:</p>
<ul>
  <li>Um <strong>alerta automático</strong> nos sistemas de prontuário eletrônico quando os campos
      de notificação sugerem alta probabilidade de violência sexual;</li>
  <li>Uma <strong>ferramenta de priorização</strong> para que enfermeiras/agentes de saúde
      identifiquem casos que precisam de encaminhamento urgente (protocolo de violência sexual
      do Ministério da Saúde).</li>
</ul>

<h2>Limitações e Cuidados Éticos</h2>
<ul>
  <li>O modelo foi treinado em notificações já <strong>registradas</strong>; casos não notificados
      (subnotificação) criam viés;</li>
  <li>Dados com muitos campos ignorados (valor 9) reduzem a qualidade das previsões;</li>
  <li>O <strong>profissional de saúde deve sempre ter a palavra final</strong> no diagnóstico;</li>
  <li>Qualquer uso deve estar em conformidade com a <strong>LGPD (Lei nº 13.709/2018)</strong>.</li>
</ul>

<h2>Próximos Passos Sugeridos</h2>
<ol>
  <li>Coleta de dados mais completa (reduzir campos 'ignorados');</li>
  <li>Validação com dados de outros anos e outras UFs;</li>
  <li>Explorar modelos interpretáveis (e.g., EBM — Explainable Boosting Machine);</li>
  <li>Integração com sistemas de prontuário eletrônico (RES/RNDS).</li>
</ol>

<!-- ══ 8. ARTEFATOS ════════════════════════════════════════════════════════════ -->
<h1>8. Artefatos do Modelo e Persistência</h1>
<table>
  <tr><th>Arquivo</th><th>Conteúdo</th></tr>
  <tr><td><code>xgb_viol_sexu.joblib</code></td><td>Modelo XGBoost treinado (classificador principal)</td></tr>
  <tr><td><code>imputer.joblib</code></td><td><code>SimpleImputer(strategy='median')</code> ajustado nos dados de treino</td></tr>
  <tr><td><code>scaler.joblib</code></td><td><code>StandardScaler</code> ajustado nos dados de treino</td></tr>
  <tr><td><code>feature_columns.joblib</code></td><td>Lista com os nomes das colunas de entrada na ordem exata</td></tr>
</table>

<p>Para carregar o modelo em outra aplicação (ex.: API Flask):</p>
<pre>
import joblib
import pandas as pd

model    = joblib.load('model/xgb_viol_sexu.joblib')
imputer  = joblib.load('model/imputer.joblib')
features = joblib.load('model/feature_columns.joblib')

# X_new deve ser um DataFrame com as mesmas colunas de 'features'
X_imputed = imputer.transform(X_new[features])
proba = model.predict_proba(X_imputed)[:, 1]   # P(violência sexual)
</pre>

<h2>Nota sobre Docker</h2>
<p>
  O repositório de Machine Learning não inclui Dockerfile — o ambiente é gerenciado via
  <code>requirements.txt</code> e executado localmente no Jupyter. O repositório da API
  (<code>Fiap_Pos_9AIDT_Fase_01_API</code>) e o repositório WEB
  (<code>Fiap_Pos_9IADT_Fase_01_WEB</code>) podem conter Dockerfiles para containerização
  dos serviços.
</p>

<!-- ══ 9. CONSIDERAÇÕES FINAIS ════════════════════════════════════════════════ -->
<h1>9. Considerações Finais</h1>
<p>
  Este Tech Challenge demonstrou a viabilidade de usar Machine Learning para apoiar a triagem
  clínica de mulheres vítimas de violência. O modelo XGBoost atingiu <strong>Recall de 88%</strong>
  e <strong>F1-Score de 79%</strong> para a classe de violência sexual, priorizando a
  identificação de casos positivos — essencial no contexto de triagem médica.
</p>
<p>A solução completa é composta por três repositórios integrados:</p>
<ul>
  <li><strong>ML:</strong> Notebook com análise exploratória, pré-processamento, treinamento
      e persistência do modelo.<br />
      Clique aqui no <strong>Link do Github</strong> = <a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_ML">Fiap_Pos_9AIDT_Fase_01_ML</a>
  </li>
  <li><strong>API:</strong> Serviço REST que carrega o modelo treinado e expõe endpoints de
      predição.<br />
      Clique aqui no <strong>Link do Github</strong> = <a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_API">Fiap_Pos_9AIDT_Fase_01_API</a>
  </li>
  <li><strong>WEB:</strong> Interface web para que profissionais de saúde realizem a triagem
      interativamente. <br />
      Clique aqui no <strong>Link do Github</strong> = <a href="https://github.com/Etyonamine/Fiap_Pos_9AIDT_Fase_01_WEB">Fiap_Pos_9AIDT_Fase_01_WEB</a>
  </li>
</ul>
<div class="warning-box">
  ⚠️ <strong>Aviso Final:</strong> Este modelo é um instrumento de apoio e não substitui o
  julgamento clínico do profissional de saúde. A decisão final de diagnóstico e encaminhamento
  é sempre responsabilidade do médico ou enfermeiro.
</div>

</body>
</html>"""


# ── Principal ──────────────────────────────────────────────────────────────────

def main():
    print("📄 Gerando relatório PDF — Tech Challenge - Fase 1")
    print(f"   Notebook: {NOTEBOOK_PATH}")
    print(f"   Saída:    {OUTPUT_FILE}")

    if not os.path.exists(NOTEBOOK_PATH):
        raise FileNotFoundError(
            f"Notebook não encontrado: {NOTEBOOK_PATH}\n"
            "Execute este script a partir da raiz do repositório."
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🔍 Extraindo imagens do notebook...")
    images = load_notebook_images(NOTEBOOK_PATH)
    print(f"   {sum(len(v) for v in images.values())} imagem(ns) extraída(s) de {len(images)} célula(s).")

    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    print("🏗️  Construindo HTML...")
    html_content = build_html(images, generated_at)

    print("🖨️  Convertendo para PDF (WeasyPrint)...")
    HTML(string=html_content, base_url=".").write_pdf(OUTPUT_FILE)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"✅ PDF gerado com sucesso: {OUTPUT_FILE} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
