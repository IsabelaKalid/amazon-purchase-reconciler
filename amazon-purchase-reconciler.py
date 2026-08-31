import pandas as pd
import os
from datetime import datetime
from collections import defaultdict
import argparse

# ==============================================================================
# CONFIGURAÇÃO DE ARGUMENTOS / ARGUMENT CONFIGURATION
# Remove caminhos absolutos hardcoded / Removes hardcoded absolute paths
# ==============================================================================
parser = argparse.ArgumentParser(
    description="Reconcile Amazon Purchase Orders / Reconciliação de Pedidos Amazon"
)
parser.add_argument(
    "--input-check",
    default="data/to_check.xlsx",
    help="Caminho do arquivo a conferir / Path to the file to check",
)
parser.add_argument(
    "--input-amazon",
    default="data/amazon_orders.xlsx",
    help="Caminho do relatório Amazon / Path to the Amazon report",
)
parser.add_argument(
    "--output-dir",
    default="output/",
    help="Diretório de saída / Output directory",
)

args = parser.parse_args()

# PT: Definir caminhos dinâmicos via argumentos de entrada
# EN: Define dynamic paths via input arguments
file_to_check = args.input_check
file_amazon = args.input_amazon
output_folder = args.output_dir

# PT: Garantir que a pasta de saída exista
# EN: Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

# ==============================================================================
# LEITURA E PADRONIZAÇÃO DE DADOS / DATA LOADING AND STANDARDIZATION
# ==============================================================================
# PT: Carregar planilhas de entrada
# EN: Load input spreadsheets
df_conferir = pd.read_excel(file_to_check)
df_amazon = pd.read_excel(file_amazon)

# PT: Padronizar cabeçalhos da planilha interna
# EN: Standardize internal spreadsheet headers
df_conferir.rename(
    columns={
        df_conferir.columns[0]: "Data",
        df_conferir.columns[1]: "Pedido",
        df_conferir.columns[2]: "Sku",
    },
    inplace=True,
)

# PT: Converter colunas chave para valores numéricos, ignorando textos inválidos
# EN: Convert key columns to numeric values, coercing invalid text to NaN
df_conferir["Pedido_num"] = pd.to_numeric(
    df_conferir["Pedido"], errors="coerce"
)
df_conferir["Sku_num"] = pd.to_numeric(df_conferir["Sku"], errors="coerce")

df_amazon["po_number_num"] = pd.to_numeric(
    df_amazon["po_number"], errors="coerce"
)
df_amazon["material_num"] = pd.to_numeric(
    df_amazon["material"], errors="coerce"
)

# PT: Remover registros com dados numéricos nulos nas chaves
# EN: Drop records with null numeric values in key fields
df_conferir_filtrado = df_conferir.dropna(
    subset=["Pedido_num", "Sku_num"]
).copy()
df_amazon_filtrado = df_amazon.dropna(
    subset=["po_number_num", "material_num"]
).copy()

# PT: Unificar tipos para inteiro para evitar falhas de divergência tipo str/float
# EN: Cast to integer to prevent mismatches caused by type discrepancies (str/float)
df_conferir_filtrado["Pedido_num"] = df_conferir_filtrado[
    "Pedido_num"
].astype(int)
df_conferir_filtrado["Sku_num"] = df_conferir_filtrado["Sku_num"].astype(int)
df_amazon_filtrado["po_number_num"] = df_amazon_filtrado[
    "po_number_num"
].astype(int)
df_amazon_filtrado["material_num"] = df_amazon_filtrado["material_num"].astype(
    int
)

# PT: Criar chave única composta (Pedido-SKU)
# EN: Create a unique composite key (Order-SKU)
df_conferir_filtrado["chave"] = (
    df_conferir_filtrado["Pedido_num"].astype(str)
    + "-"
    + df_conferir_filtrado["Sku_num"].astype(str)
)
df_amazon_filtrado["chave"] = (
    df_amazon_filtrado["po_number_num"].astype(str)
    + "-"
    + df_amazon_filtrado["material_num"].astype(str)
)

# ==============================================================================
# ESTRUTURAÇÃO DA BUSCA / SEARCH MAP PREPARATION
# ==============================================================================
# PT: Mapear pedidos para seus respectivos materiais cadastrados na Amazon
# EN: Map orders to their respective listed materials in Amazon data
amazon_pedido_para_materials = defaultdict(set)
for _, row in df_amazon_filtrado.iterrows():
    amazon_pedido_para_materials[row["po_number_num"]].add(row["material_num"])

# Set para busca em complexidade O(1)
# Set lookup for O(1) complexity
amazon_chaves_set = set(df_amazon_filtrado["chave"])
amazon_pedidos_set = set(df_amazon["po_number_num"].dropna().astype(int))


def definir_motivo(row):
    """PT: Identifica inconsistências entre o pedido interno e os dados da Amazon.

    EN: Identifies discrepancies between internal orders and Amazon report
    data.
    """
    pedido = row["Pedido_num"]
    sku = row["Sku_num"]
    chave = f"{pedido}-{sku}"

    # PT: Correspondência exata encontrada (Pedido + SKU)
    # EN: Exact match found (Order + SKU)
    if chave in amazon_chaves_set:
        return ""

    # PT: O pedido não existe no relatório da Amazon
    # EN: Order ID not found in Amazon report
    if pedido not in amazon_pedidos_set:
        return "Pedido não encontrado / Order not found"

    # PT: Pedido localizado, mas sem código de material preenchido
    # EN: Order found, but material field is empty
    materiais_pedido = df_amazon[df_amazon["po_number_num"] == pedido][
        "material_num"
    ]
    if not materiais_pedido.dropna().any():
        return "Sku vazio / Empty SKU"

    # PT: Pedido localizado, porém com divergência no SKU registrado
    # EN: Order found, but recorded SKU differs
    if pedido in amazon_pedido_para_materials:
        materiais_amazon = amazon_pedido_para_materials[pedido]
        if sku not in materiais_amazon:
            materiais_str = ", ".join(str(m) for m in sorted(materiais_amazon))
            return f"Sku diferente no relatório: {materiais_str} / Divergent SKU: {materiais_str}"

    return "Pedido não encontrado / Order not found"


# ==============================================================================
# EXECUÇÃO E SAÍDA / EXECUTION AND OUTPUT
# ==============================================================================
# PT: Processar divergências
# EN: Process discrepancies
df_conferir_filtrado["Motivo"] = df_conferir_filtrado.apply(
    definir_motivo, axis=1
)

resultado = df_conferir_filtrado[["Data", "Pedido", "Sku", "Motivo"]]
resultado_filtrado = resultado[resultado["Motivo"] != ""].copy()

# PT: Gerar arquivo de saída sem risco de sobrescrita
# EN: Generate non-destructive output filename using timestamp
arquivo_saida = os.path.join(output_folder, "divergencias_pedidos.xlsx")
if os.path.exists(arquivo_saida):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_saida = os.path.join(
        output_folder, f"divergencias_pedidos_{timestamp}.xlsx"
    )

resultado_filtrado.to_excel(arquivo_saida, index=False)

print(f"[SUCCESS] Processamento concluído. / Processing complete.")
print(f"Relatório de divergências salvo em / Saved to: {arquivo_saida}")
print(f"Total de inconsistências / Total discrepancies: {len(resultado_filtrado)}")