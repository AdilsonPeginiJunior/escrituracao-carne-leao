#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validação do gerador de relatórios.
Busca o primeiro recibo em uma pasta de profissional e verifica a geração do PDF.
"""

import json
import os
from pathlib import Path
from models.report_generator import ReportGenerator, RecibosReportManager, ReportDataExtractor
from models.storage import sanitize_profissional_name


def find_profissional_folder_for_recibo(recibo):
    root = Path(__file__).resolve().parent
    cpf_procurado = recibo.get('cpf_benef') if recibo.get('cpf_benef') and recibo.get('cpf_benef') != recibo.get('cpf_pagador') else recibo.get('cpf_pagador')
    if not cpf_procurado:
        return root / 'profissionais'

    cpf_digits = ''.join(ch for ch in str(cpf_procurado) if ch.isdigit())
    prof_file = root / 'profissionais.json'
    if prof_file.exists():
        with open(prof_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for prof in data.get('profissionais', []):
            if ''.join(ch for ch in str(prof.get('cpf_prof', '')) if ch.isdigit()) == cpf_digits:
                candidate = root / 'profissionais' / sanitize_profissional_name(prof.get('apelido', ''))
                if candidate.exists():
                    return candidate

    for folder in (root / 'profissionais').glob('*'):
        if not folder.is_dir():
            continue
        pacientes_file = folder / 'pacientes.json'
        if not pacientes_file.exists():
            continue
        try:
            with open(pacientes_file, 'r', encoding='utf-8') as f:
                pacientes = json.load(f).get('pacientes', [])
            if any(
                p.get('cpf_benef') == cpf_procurado or p.get('cpf_pagador') == cpf_procurado
                for p in pacientes
            ):
                return folder
        except Exception:
            continue

    return root / 'profissionais'


def main():
    """Gera relatório com dados do primeiro recibo"""

    print("=" * 60)
    print("GERANDO RELATÓRIO COM DADOS DO PRIMEIRO RECIBO")
    print("=" * 60)

    try:
        root = Path(__file__).resolve().parent
        professional_dir = root / 'profissionais'
        if not professional_dir.exists():
            print('Diretório de profissionais não encontrado')
            return

        recibos_candidates = []
        for folder in professional_dir.glob('*'):
            if folder.is_dir():
                recibos_file = folder / 'recibos_saude.json'
                if recibos_file.exists():
                    with open(recibos_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    for recibo in data.get('recibos', []):
                        recibos_candidates.append((folder, recibo))

        if not recibos_candidates:
            print('Nenhum recibo encontrado em pastas de profissionais')
            return

        professional_dir, primeiro_recibo = recibos_candidates[0]
        recibos_path = professional_dir / 'recibos_saude.json'
        with open(recibos_path, 'r', encoding='utf-8') as f:
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

        pacientes_path = professional_dir / 'pacientes.json'
        if pacientes_path.exists():
            try:
                with open(pacientes_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                pacientes = data.get('pacientes', [])

                for p in pacientes:
                    cpf_b = p.get('cpf_benef', '').strip()
                    cpf_p = p.get('cpf_pagador', '').strip()

                    if cpf_b == cpf_procurado or cpf_p == cpf_procurado:
                        paciente = p
                        break
            except Exception as e:
                pass

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
