#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste do gerador de relatórios
Valida a extração de variáveis e a estrutura base do gerador
"""

import json
from models.report_generator import ReportDataExtractor

# Dados de teste
recibo_teste = {
    "data": "15/04/2026",
    "valor": "400,00",
    "cpf_pagador": "39111825898",
    "cpf_benef": "39111825898",
    "descricao": "Referente a 04 sessões de psicoterapia realizadas nos dias 06/04/2026, 13/04/2026, 20/04/2026 e 27/04/2026.",
    "codigo": "R01.001.001",
    "inscricao": "06/146439",
    "tipo_pagador": "PF",
    "registro": "06/23007",
    "cpf_prof": "21916589898",
    "id": 1777059988818,
    "data_criacao": "2026-04-24T16:46:28.818885",
    "data_atualizacao": "2026-05-01T14:57:22.642595"
}

paciente_teste = {
    "nome_pagador": "Ana Paula Costa Xavier",
    "cpf_pagador": "39111825898",
    "nome_benef": "",
    "cpf_benef": "",
    "valor_cons": "100,00",
    "cod_cid": "F 41",
    "inicio": "26/10/2023",
    "genero": "Fem",
    "gera_relatorio": "",
    "id": 1769471295219,
    "data_criacao": "2026-01-26T20:48:15.219569",
    "data_atualizacao": "2026-05-01T16:26:28.029696"
}

print("=" * 70)
print("TESTE DO GERADOR DE RELATÓRIOS")
print("=" * 70)

# Teste 1: Extração de número de sessões
print("\n[TESTE 1] Extração de número de sessões")
descricao = recibo_teste["descricao"]
nr_sessoes = ReportDataExtractor.extract_sessions_from_description(descricao)
print(f"Descrição: {descricao}")
print(f"Número de sessões extraído: {nr_sessoes}")
assert nr_sessoes == 4, f"Esperava 4 sessões, obteve {nr_sessoes}"
print("✓ PASSOU")

# Teste 2: Extração de datas
print("\n[TESTE 2] Extração de datas das consultas")
datas, primeira_data = ReportDataExtractor.extract_dates_from_description(
    descricao)
print(f"Datas extraídas: {datas}")
print(f"Primeira data: {primeira_data}")
assert len(datas) == 4, f"Esperava 4 datas, obteve {len(datas)}"
assert primeira_data == "06/04/2026", f"Esperava primeira data 06/04/2026, obteve {primeira_data}"
print("✓ PASSOU")

# Teste 3: Parse de data
print("\n[TESTE 3] Parse de data DD/MM/YYYY")
dia, mes, ano = ReportDataExtractor.parse_date("06/04/2026")
print(f"Data: 06/04/2026 -> Dia: {dia}, Mês: {mes}, Ano: {ano}")
assert dia == 6 and mes == 4 and ano == 2026, "Parse de data incorreto"
print("✓ PASSOU")

# Teste 4: Último dia do mês
print("\n[TESTE 4] Cálculo do último dia do mês")
ult_dia = ReportDataExtractor.get_last_day_of_month(6, 4, 2026)
print(f"Abril de 2026 tem {ult_dia} dias")
assert ult_dia == 30, f"Esperava 30 dias em abril, obteve {ult_dia}"
print("✓ PASSOU")

# Teste 5: Mês por extenso
print("\n[TESTE 5] Mês por extenso")
mes_extenso = ReportDataExtractor.MESES_EXTENSO[4]
print(f"Mês 4 = {mes_extenso}")
assert mes_extenso == "abril", f"Esperava 'abril', obteve {mes_extenso}"
print("✓ PASSOU")

# Teste 6: Extração completa de variáveis
print("\n[TESTE 6] Extração completa de variáveis do relatório")
variables = ReportDataExtractor.extract_report_variables(
    recibo_teste, paciente_teste)

print("\nVariáveis extraídas:")
for var_name, var_value in variables.items():
    print(f"  {var_name}: {var_value}")

# Validações
assert variables['#NomePac'] == "Ana Paula Costa Xavier", "Nome do paciente incorreto"
assert variables['#CPF'] == "39111825898", "CPF incorreto"
assert variables['#NrSessoes'] == "4", "Número de sessões incorreto"
assert variables['#DataDasCons'] == "06/04/2026, 13/04/2026, 20/04/2026 e 27/04/2026", "Datas incorretas"
assert variables['#UltDiaMesConsultas'] == "30", "Último dia do mês incorreto"
assert variables['#MesDasConsultas2'] == "abril", "Mês incorreto"
assert variables['#AnoDasConsultas2'] == "2026", "Ano incorreto"

print("\n✓ PASSOU")

# Teste 7: Caso com beneficiário diferente
print("\n[TESTE 7] Extração com beneficiário diferente de pagador")
paciente_com_benef = paciente_teste.copy()
paciente_com_benef['nome_benef'] = "Danilo Malagosini Machado Borba"
paciente_com_benef['cpf_benef'] = "43410629807"

recibo_com_benef = recibo_teste.copy()
recibo_com_benef['cpf_benef'] = "43410629807"

variables_benef = ReportDataExtractor.extract_report_variables(
    recibo_com_benef, paciente_com_benef)
print(f"  #NomePac (beneficiário): {variables_benef['#NomePac']}")
print(f"  #CPF (beneficiário): {variables_benef['#CPF']}")
assert variables_benef['#NomePac'] == "Danilo Malagosini Machado Borba", "Nome do beneficiário incorreto"
assert variables_benef['#CPF'] == "43410629807", "CPF do beneficiário incorreto"
print("✓ PASSOU")

print("\n" + "=" * 70)
print("TODOS OS TESTES PASSARAM COM SUCESSO! ✓")
print("=" * 70)
print("\nO gerador de relatórios está pronto para uso.")
print("Integração com a UI concluída.")
print("\nPróximos passos:")
print("1. Abra a aplicação e clique em 'Gerar Relatórios' na aba 'Receita Saúde'")
print("2. Selecione um recibo da lista")
print("3. Clique em 'Gerar Relatório' para criar o PDF")
print("4. O arquivo será salvo na pasta especificada (padrão: Desktop)")
