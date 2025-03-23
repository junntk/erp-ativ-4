import streamlit as st
import pandas as pd
import sqlite3
from faker import Faker
from datetime import datetime
import altair as alt


# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Relatórios Financeiros")
        st.subheader("Distribuição das Contas a Pagar por Fornecedor")
        df_pagar = pd.read_sql_query("SELECT fornecedor, SUM(valor) as total FROM contas_pagar GROUP BY fornecedor", conn)

        if not df_pagar.empty:
            chart_pagar = alt.Chart(df_pagar).mark_bar().encode(
                x=alt.X("total", title="Total devido"),
                y=alt.Y("fornecedor", sort="-x", title="Fornecedor"),
                color=alt.Color("fornecedor", legend=None)
            )
            st.altair_chart(chart_pagar, use_container_width=True)
        else:
            st.warning("Nenhuma conta a pagar cadastrada.")
        st.subheader("Top 5 Clientes com Maior Receita")
        query_top_clientes = """
            SELECT c.nome AS Cliente, SUM(cr.valor) AS Receita
            FROM contas_receber cr
            JOIN clientes c ON cr.cliente_id = c.id
            WHERE cr.status = 'Recebido'
            GROUP BY cr.cliente_id
            ORDER BY Receita DESC
            LIMIT 5
        """
        df_top_clientes = pd.read_sql_query(query_top_clientes, conn)

        if not df_top_clientes.empty:
            st.dataframe(df_top_clientes)

            chart_receita = alt.Chart(df_top_clientes).mark_bar().encode(
                x=alt.X("Receita:Q", title="Total Recebido"),
                y=alt.Y("Cliente:N", sort="-x", title="Clientes"),
                color=alt.value("#4C78A8")
            ).properties(
                title="Top 5 Clientes com Maior Receita"
            )

            st.altair_chart(chart_receita, use_container_width=True)
        else:
            st.warning("Nenhuma receita recebida cadastrada.")
        st.subheader("Comparação Receita vs Despesa - Mês Atual")
        mes_atual = datetime.now().strftime('%Y-%m')

        query_fluxo_mes = f"""
            SELECT 
                SUM(CASE WHEN tipo = 'Receita' THEN valor ELSE 0 END) as Receita,
                SUM(CASE WHEN tipo = 'Despesa' THEN valor ELSE 0 END) as Despesa
            FROM lancamentos 
            WHERE strftime('%Y-%m', data) = '{mes_atual}'
        """
        df_fluxo_mes = pd.read_sql_query(query_fluxo_mes, conn)

        if not df_fluxo_mes.empty and (df_fluxo_mes.iloc[0]['Receita'] > 0 or df_fluxo_mes.iloc[0]['Despesa'] > 0):
            df_fluxo_mes = df_fluxo_mes.melt(var_name="Categoria", value_name="Valor")

            chart_fluxo_mes = alt.Chart(df_fluxo_mes).mark_bar().encode(
                x=alt.X("Categoria:N", title=""),
                y=alt.Y("Valor:Q", title="Valor (R$)"),
                color=alt.Color("Categoria:N", scale=alt.Scale(domain=['Receita', 'Despesa'], range=['green', 'red']))
            ).properties(
                title=f"Receita vs Despesa - {mes_atual}"
            )

            st.altair_chart(chart_fluxo_mes, use_container_width=True)
        else:
            st.warning("Nenhuma movimentação financeira registrada para este mês.")

    conn.close()
    
if __name__ == "__main__":
    main()
