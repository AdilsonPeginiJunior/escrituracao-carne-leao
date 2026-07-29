import re
from models.report_generator import ReportDataExtractor
from datetime import datetime
import json
import os
from models.report_generator import ReportGenerator

CPF = '43795607833'
# Carregar recibos
with open('recibos_saude.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    recibos = data.get('recibos', [])

recibo = None
for r in recibos:
    if r.get('cpf_pagador') == CPF or r.get('cpf_benef') == CPF:
        recibo = r
        break

if not recibo:
    print('Recibo não encontrado')
    exit(1)

# Carregar paciente
# procurar arquivo _pacientes.json que contenha o CPF
paciente = None
for file in os.listdir('.'):
    if file.endswith('_pacientes.json'):
        try:
            with open(file, 'r', encoding='utf-8') as pf:
                pd = json.load(pf)
                for p in pd.get('pacientes', []):
                    if p.get('cpf_pagador') == CPF or p.get('cpf_benef') == CPF:
                        paciente = p
                        break
        except Exception:
            continue
    if paciente:
        break

if not paciente:
    print('Paciente não encontrado')
    exit(1)

# Definir template existente (com underscore)
template = os.path.join('modelosRelatorios',
                        '_RelatorioTemplateCarimboFem.docx')
if not os.path.exists(template):
    print('Template não encontrado:', template)
    exit(1)

# Definir pasta de saída (Desktop/Relatório de Maio etc.)
variables = ReportGenerator(
    template).replace_text_in_document if False else None
# Use ReportGenerator to build filename similar ao UI
vars = ReportDataExtractor.extract_report_variables(recibo, paciente)
nome_benef = vars.get('#NomePac', 'Paciente')
ano = vars.get('#AnoDasConsultas2', '')
mes = vars.get('#MesDasConsultas2', '')
if not mes:
    mes = datetime.now().strftime('%B')
mes_cap = mes.capitalize()
output_folder = os.path.expanduser('~/Desktop')
pasta_mes = f'Relatório de {mes_cap}'
caminho_mes = os.path.join(output_folder, pasta_mes)
if not os.path.exists(caminho_mes):
    os.makedirs(caminho_mes, exist_ok=True)

nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome_benef).strip()
output_filename = f"{nome_limpo} - Relatório {ano}{mes.capitalize()}.pdf"
output_path = os.path.join(caminho_mes, output_filename)

print('Gerando em:', output_path)

rg = ReportGenerator(template)
success = rg.generate_report(recibo, paciente, output_path)
print('Sucesso:', success)
