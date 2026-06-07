import streamlit as st
import json
import os
from datetime import datetime

# ── configuração da página ──────────────────────────────────────
st.set_page_config(page_title="Marcenaria", page_icon="🪵", layout="wide")

ARQUIVO_DADOS = "dados_marcenaria.json"

# ── funções de dados ────────────────────────────────────────────
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"produtos": [], "clientes": [], "orcamentos": [], "vendas": []}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ── carrega os dados ────────────────────────────────────────────
dados = carregar_dados()

# ── menu lateral ────────────────────────────────────────────────
st.sidebar.title("🪵 Marcenaria")
pagina = st.sidebar.radio("Menu", ["Clientes", "Produtos", "Orçamentos", "Vendas"])

# ══════════════════════════════════════════════════════════════
# PÁGINA: CLIENTES
# ══════════════════════════════════════════════════════════════
if pagina == "Clientes":
    st.title("👤 Clientes")

    with st.expander("➕ Adicionar novo cliente"):
        nome     = st.text_input("Nome")
        telefone = st.text_input("Telefone")
        email    = st.text_input("Email")

        if st.button("Salvar cliente"):
            if nome.strip() == "":
                st.error("O nome é obrigatório.")
            else:
                novo = {
                    "id": len(dados["clientes"]) + 1,
                    "nome": nome,
                    "telefone": telefone,
                    "email": email,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y")
                }
                dados["clientes"].append(novo)
                salvar_dados(dados)
                st.success(f"Cliente '{nome}' cadastrado!")
                st.rerun()

    st.subheader("Clientes cadastrados")
    if not dados["clientes"]:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        for c in dados["clientes"]:
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(f"**{c['nome']}**")
            col2.write(c['telefone'])
            col3.write(c['email'])

# ══════════════════════════════════════════════════════════════
# PÁGINA: PRODUTOS
# ══════════════════════════════════════════════════════════════
elif pagina == "Produtos":
    st.title("📦 Produtos")

    with st.expander("➕ Adicionar novo produto"):
        nome_prod     = st.text_input("Nome do produto")
        preco_prod    = st.number_input("Preço unitário (R$)", min_value=0.0, format="%.2f")
        descricao_prod = st.text_input("Descrição")

        if st.button("Salvar produto"):
            if nome_prod.strip() == "":
                st.error("O nome é obrigatório.")
            else:
                novo_prod = {
                    "id": len(dados["produtos"]) + 1,
                    "nome": nome_prod,
                    "preco": preco_prod,
                    "descricao": descricao_prod
                }
                dados["produtos"].append(novo_prod)
                salvar_dados(dados)
                st.success(f"Produto '{nome_prod}' cadastrado!")
                st.rerun()

    st.subheader("Produtos cadastrados")
    if not dados["produtos"]:
        st.info("Nenhum produto cadastrado ainda.")
    else:
        for p in dados["produtos"]:
            col1, col2, col3 = st.columns([3, 2, 3])
            col1.write(f"**{p['nome']}**")
            col2.write(f"R$ {p['preco']:.2f}")
            col3.write(p['descricao'])

# ══════════════════════════════════════════════════════════════
# PÁGINA: ORÇAMENTOS
# ══════════════════════════════════════════════════════════════
elif pagina == "Orçamentos":
    st.title("📋 Orçamentos")

    aba1, aba2 = st.tabs(["➕ Novo orçamento", "📄 Orçamentos salvos"])

    with aba1:
        if not dados["clientes"]:
            st.warning("Cadastre um cliente antes de criar um orçamento.")
        elif not dados["produtos"]:
            st.warning("Cadastre um produto antes de criar um orçamento.")
        else:
            nomes_clientes = [c["nome"] for c in dados["clientes"]]
            cliente_escolhido = st.selectbox("Cliente", nomes_clientes)

            st.subheader("Itens do orçamento")

            if "num_itens" not in st.session_state:
                st.session_state.num_itens = 1

            col_add, col_rem = st.columns([1, 1])
            if col_add.button("+ Adicionar item"):
                st.session_state.num_itens += 1
            if col_rem.button("- Remover item") and st.session_state.num_itens > 1:
                st.session_state.num_itens -= 1

            nomes_produtos = [p["nome"] for p in dados["produtos"]]
            itens = []
            total = 0.0

            for i in range(st.session_state.num_itens):
                st.markdown(f"**Item {i+1}**")
                col1, col2, col3 = st.columns([3, 1, 2])
                prod_nome = col1.selectbox("Produto", nomes_produtos, key=f"prod_{i}")
                qtd       = col2.number_input("Qtd", min_value=1, value=1, key=f"qtd_{i}")
                prod      = next(p for p in dados["produtos"] if p["nome"] == prod_nome)
                subtotal  = prod["preco"] * qtd
                col3.metric("Subtotal", f"R$ {subtotal:.2f}")

                itens.append({
                    "produto_nome":   prod_nome,
                    "preco_unitario": prod["preco"],
                    "quantidade":     qtd,
                    "subtotal":       subtotal
                })
                total += subtotal

            st.divider()
            desconto    = st.number_input("Desconto (R$)", min_value=0.0, format="%.2f")
            valor_final = total - desconto

            col_t1, col_t2 = st.columns(2)
            col_t1.metric("Total bruto", f"R$ {total:.2f}")
            col_t2.metric("Valor final", f"R$ {valor_final:.2f}")

            if st.button("💾 Salvar orçamento"):
                orcamento = {
                    "id":           len(dados["orcamentos"]) + 1,
                    "cliente_nome": cliente_escolhido,
                    "data":         datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "itens":        itens,
                    "total":        total,
                    "desconto":     desconto,
                    "valor_final":  valor_final,
                    "status":       "Pendente"
                }
                dados["orcamentos"].append(orcamento)
                salvar_dados(dados)
                st.success("Orçamento salvo!")
                st.session_state.num_itens = 1
                st.rerun()

    with aba2:
        if not dados["orcamentos"]:
            st.info("Nenhum orçamento criado ainda.")
        else:
            for o in dados["orcamentos"]:
                status_cor = "🟡" if o["status"] == "Pendente" else "🟢"
                with st.expander(f"{status_cor} #{o['id']} — {o['cliente_nome']} — R$ {o['valor_final']:.2f} — {o['data']}"):
                    for item in o["itens"]:
                        st.write(f"• {item['quantidade']}x {item['produto_nome']} — R$ {item['subtotal']:.2f}")
                    st.write(f"**Total bruto:** R$ {o['total']:.2f}")
                    if o["desconto"] > 0:
                        st.write(f"**Desconto:** R$ {o['desconto']:.2f}")
                    st.write(f"**Valor final:** R$ {o['valor_final']:.2f}")
                    st.write(f"**Status:** {o['status']}")

                    if o["status"] == "Pendente":
                        if st.button("✅ Converter em venda", key=f"venda_{o['id']}"):
                            venda = {
                                "id":              len(dados["vendas"]) + 1,
                                "orcamento_id":    o["id"],
                                "cliente_nome":    o["cliente_nome"],
                                "data":            datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "itens":           o["itens"],
                                "valor_original":  o["total"],
                                "desconto":        o["desconto"],
                                "valor_final":     o["valor_final"],
                                "forma_pagamento": "A definir"
                            }
                            dados["vendas"].append(venda)
                            o["status"] = "Vendido"
                            salvar_dados(dados)
                            st.success("Venda registrada!")
                            st.rerun()
 
 # ══════════════════════════════════════════════════════════════
# PÁGINA: VENDAS
# ══════════════════════════════════════════════════════════════
elif pagina == "Vendas":
    st.title("💰 Vendas")

    if not dados["vendas"]:
        st.info("Nenhuma venda registrada ainda.")
    else:
        # ── métricas no topo ─────────────────────────────────
        total_geral  = sum(v["valor_final"] for v in dados["vendas"])
        ticket_medio = total_geral / len(dados["vendas"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de vendas", len(dados["vendas"]))
        col2.metric("Faturamento total", f"R$ {total_geral:.2f}")
        col3.metric("Ticket médio", f"R$ {ticket_medio:.2f}")

        st.divider()

        # ── lista de vendas ───────────────────────────────────
        for v in dados["vendas"]:
            with st.expander(f"🟢 Venda #{v['id']} — {v['cliente_nome']} — R$ {v['valor_final']:.2f} — {v['data']}"):
                for item in v["itens"]:
                    st.write(f"• {item['quantidade']}x {item['produto_nome']} — R$ {item['subtotal']:.2f}")
                st.write(f"**Valor original:** R$ {v['valor_original']:.2f}")
                if v["desconto"] > 0:
                    st.write(f"**Desconto:** R$ {v['desconto']:.2f}")
                st.write(f"**Valor final:** R$ {v['valor_final']:.2f}")
                st.write(f"**Pagamento:** {v['forma_pagamento']}")