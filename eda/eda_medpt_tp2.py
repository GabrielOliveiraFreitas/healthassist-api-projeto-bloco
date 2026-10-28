import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu

df = pd.read_csv("medpt_amostra.csv")

# features numericas derivadas do texto, usadas na correlacao e nos scatter plots
df["tam_pergunta_palavras"] = df["question"].apply(lambda x: len(str(x).split()))
df["tam_resposta_palavras"] = df["answer"].apply(lambda x: len(str(x).split()))
df["tam_pergunta_caracteres"] = df["question"].apply(lambda x: len(str(x)))
df["tam_resposta_caracteres"] = df["answer"].apply(lambda x: len(str(x)))
df["palavras_unicas_pergunta"] = df["question"].apply(lambda x: len(set(str(x).lower().split())))
df["razao_resposta_pergunta"] = df["tam_resposta_palavras"] / df["tam_pergunta_palavras"]

colunas_numericas = [
    "tam_pergunta_palavras",
    "tam_resposta_palavras",
    "tam_pergunta_caracteres",
    "tam_resposta_caracteres",
    "palavras_unicas_pergunta",
    "razao_resposta_pergunta",
]

# heatmap de correlacao
plt.figure(figsize=(8, 6))
sns.heatmap(df[colunas_numericas].corr(), annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlacao entre variaveis numericas derivadas do texto")
plt.tight_layout()
plt.savefig("heatmap_correlacao.png")
plt.close()

# scatter 1: tamanho da pergunta vs tamanho da resposta
plt.figure(figsize=(8, 6))
plt.scatter(df["tam_pergunta_palavras"], df["tam_resposta_palavras"], alpha=0.3, s=15)
plt.xlabel("Tamanho da pergunta (palavras)")
plt.ylabel("Tamanho da resposta (palavras)")
plt.title("Tamanho da pergunta vs tamanho da resposta")
plt.tight_layout()
plt.savefig("scatter_pergunta_resposta.png")
plt.close()

# scatter 2: tamanho em caracteres vs palavras unicas (riqueza de vocabulario)
plt.figure(figsize=(8, 6))
plt.scatter(df["tam_pergunta_caracteres"], df["palavras_unicas_pergunta"], alpha=0.3, s=15, color="darkorange")
plt.xlabel("Tamanho da pergunta (caracteres)")
plt.ylabel("Palavras unicas na pergunta")
plt.title("Tamanho da pergunta vs riqueza de vocabulario")
plt.tight_layout()
plt.savefig("scatter_caracteres_vocabulario.png")
plt.close()

print("heatmap e scatter plots salvos")
print()
print("matriz de correlacao:")
print(df[colunas_numericas].corr().round(2))

# teste de hipotese formal: perguntas de Diagnostico sao mais longas que as de Estilo de vida saudavel
# hipotese levantada no TP1
grupo_diagnostico = df[df["question_type"] == "Diagnóstico"]["tam_pergunta_palavras"]
grupo_estilo_vida = df[df["question_type"] == "Estilo de vida saudável"]["tam_pergunta_palavras"]

print()
print("teste de hipotese: Diagnostico vs Estilo de vida saudavel (tamanho da pergunta)")
print("n Diagnostico:", len(grupo_diagnostico), "| mediana:", grupo_diagnostico.median())
print("n Estilo de vida:", len(grupo_estilo_vida), "| mediana:", grupo_estilo_vida.median())

stat, p_valor = mannwhitneyu(grupo_diagnostico, grupo_estilo_vida, alternative="greater")
print("estatistica U:", stat)
print("p-valor:", p_valor)

if p_valor < 0.05:
    print("resultado: diferenca estatisticamente significativa (p < 0.05)")
else:
    print("resultado: nao ha evidencia estatistica suficiente (p >= 0.05)")
