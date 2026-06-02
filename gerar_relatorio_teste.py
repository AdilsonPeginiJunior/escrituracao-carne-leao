#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gerar relatório PDF com dados do primeiro recibo
"""

import json
import os
from models.report_generator import ReportGenerator, RecibosReportManager, ReportDataExtractor


def main():
    """Gera relatório com dados do primeiro recibo"""

    print("=" * 60)
    print("GERANDO RELATÓRIO COM DADOS DO PRIMEIRO RECIBO")
    print("=" * 60)

    try:
        # Carregar dados do primeiro recibo
        with open('recibos_saude.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            primeiro_recibo = data['recibos'][0]

        print(f"Recibo ID: {primeiro_recibo['id']}")
        print(f"CPF Pagador: {primeiro_recibo['cpf_pagador']}")
        print(f"CPF Beneficiário: {primeiro_recibo['cpf_benef']}")
        print(f"Descrição: {primeiro_recibo['descricao']}")

        # Procurar paciente correspondente
        paciente = None
        cpf_procurado = primeiro_recibo['cpf_benef'] if primeiro_recibo[
            'cpf_benef'] != primeiro_recibo['cpf_pagador'] else primeiro_recibo['cpf_pagador']

        # Procurar em arquivos de pacientes
        for file in os.listdir("."):
            if file.endswith("_pacientes.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        pacientes = data.get('pacientes', [])

                        for p in pacientes:
                            cpf_b = p.get('cpf_benef', '').strip()
                            cpf_p = p.get('cpf_pagador', '').strip()

                            if cpf_b == cpf_procurado or cpf_p == cpf_procurado:
                                paciente = p
                                break
                except Exception as e:
                    continue

            if paciente:
                break

        if not paciente:
            print("Erro: Paciente não encontrado!")
            return

        print(f"Paciente encontrado: {paciente['nome_pagador']}")

        # Extrair variáveis do relatório
        variables = ReportDataExtractor.extract_report_variables(
            primeiro_recibo, paciente)

        print("\nVariáveis extraídas:")
        for var_name, var_value in variables.items():
            print(f"  {var_name}: {var_value}")

        # Criar diretório de saída se não existir
        output_dir = "Relatórios"
        os.makedirs(output_dir, exist_ok=True)

        # Gerar nome do arquivo
        nome_beneficiario = variables['#NomePac']
        ano = variables['#AnoDasConsultas2']
        mes_numerico = variables.get(
            '#MesNumerico', '04')  # fallback para abril

        # Limpar nome para usar como filename
        import re
        nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome_beneficiario).strip()

        output_filename = f"{nome_limpo} - Relatório {ano}{mes_numerico}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        print(f"\nArquivo de saída: {output_path}")

        # Gerar relatório
        report_gen = ReportGenerator()
        success = report_gen.generate_report(
            primeiro_recibo, paciente, output_path)

        if success:
            print("\n✅ RELATÓRIO GERADO COM SUCESSO!")
            print(f"📄 Arquivo: {output_path}")

            # Verificar se arquivo existe
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📊 Tamanho: {file_size} bytes")
            else:
                print("⚠️  Arquivo não encontrado após geração")
        else:
            print("\n❌ ERRO AO GERAR RELATÓRIO!")

    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
