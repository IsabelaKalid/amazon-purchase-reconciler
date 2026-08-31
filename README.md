# Amazon Purchase Reconciler

[PT-BR] Ferramenta em Python para reconciliação automática de pedidos de compra (PO) e SKUs entre dados de auditoria interna e relatórios de fornecedor da Amazon.

[EN] Python tool designed to automate the cross-reconciliation of purchase orders (POs) and SKUs between internal tracking records and Amazon supplier reports.

---

## 📌 Funcionalidades / Features

* **Validação Cruzada / Cross-Validation:** Cruza a chave composta `PO + SKU` para identificar correspondências de forma eficiente.
* **Detecção de Divergências / Discrepancy Detection:**

  * Pedidos ausentes / Missing POs.
  * SKUs divergentes, exibindo o SKU encontrado no relatório.
  * Registros sem SKU / Empty SKU fields.
* **Saída Segura / Safe Output:** Evita sobrescritas utilizando timestamps automáticos nos arquivos de auditoria.
* **Relatório de Auditoria / Audit Report:** Gera arquivos Excel com os resultados da reconciliação.

---

## 🛠️ Tecnologias / Tech Stack

* **Python 3.x**
* **Pandas** — processamento e comparação dos dados
* **OpenPyXL** — leitura e geração de arquivos Excel

---

## 📦 Instalação / Installation

### Clonar o repositório / Clone the repository

```bash
git clone https://github.com/IsabelaKalid/amazon-purchase-reconciler.git
cd amazon-purchase-reconciler
```

### Instalar dependências / Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Execução / Usage

Execute o script principal:

```bash
python amazon-purchase-reconciler.py
```

O processo realiza a leitura das bases, cruza os registros utilizando `PO + SKU`, identifica divergências e gera o relatório final de auditoria.

---

## 🎯 Objetivo / Objective

### 🇧🇷 Português

Automatizar a conferência entre registros internos de compras e relatórios de fornecedores, reduzindo validações manuais e facilitando a identificação de inconsistências em pedidos e SKUs.

### 🇺🇸 English

Automate the reconciliation between internal purchasing records and supplier reports, reducing manual validation and making inconsistencies in purchase orders and SKUs easier to identify.

---

## ⚠️ Disclaimer

Este projeto foi desenvolvido para fins de demonstração de automação, processamento de dados e reconciliação de informações em arquivos Excel.

This project was developed for demonstration purposes, focusing on automation, data processing, and Excel-based data reconciliation.
