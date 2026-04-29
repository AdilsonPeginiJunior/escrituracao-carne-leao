import csv
from typing import List, Dict


class ReceitaSaudeManager:
    """Gerenciador de receitas de saúde para Carnê Leão"""

    def __init__(self):
        self.receitas: List[Dict] = []

    def add_receita(self, data: Dict) -> None:
        """Adiciona uma receita à lista"""
        self.receitas.append(data)

    def clear(self) -> None:
        """Limpa todas as receitas"""
        self.receitas = []

    def export_csv(self, file_path: str) -> None:
        """
        Exporta as receitas para um arquivo CSV
        Formato compatível com Receita Federal - Recibos de Receita Saúde
        Padrão: Data;Código;Inscrição;Valor;;Descrição;Tipo;CPF Pagador;CPF Benef;;;;S;CPF Prof;TIPO
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            # Escrever dados (SEM cabeçalho, conforme padrão da Receita Federal)
            for receita in self.receitas:
                row = [
                    # Campo 1: Data (dd/mm/aaaa)
                    receita.get('data', ''),
                    # Campo 2: Código de Receita
                    'R01.001.001',
                    # Campo 3: Inscrição
                    '255',
                    # Campo 4: Valor
                    receita.get('valor', ''),
                    '',                                          # Campo 5: Vazio
                    # Campo 6: Descrição
                    receita.get('descricao', ''),
                    # Campo 7: Tipo Pagador
                    'PF',
                    # Campo 8: CNPJ/CPF Pagador
                    receita.get('cpf_pagador', ''),
                    # Campo 9: CNPJ/CPF Profissional (CPF do Beneficiário)
                    receita.get('cpf_benef') if receita.get('cpf_benef') else receita.get('cpf_pagador', ''),
                    '',                                          # Campo 10: Vazio
                    '',                                          # Campo 11: Vazio
                    '',                                          # Campo 12: Vazio
                    '',                                          # Campo 13: Vazio
                    'S',                                         # Campo 14: S
                    # Campo 15: CPF Profissional
                    receita.get('cpf_prof', ''),
                    # Campo 16: Tipo Registro
                    receita.get('inscricao', '')
                ]
                writer.writerow(row)

    def get_stats(self) -> Dict:
        """Retorna estatísticas das receitas"""
        total = sum(
            float(r.get('valor', '0').replace(',', '.'))
            for r in self.receitas
        )
        return {
            'total_receitas': len(self.receitas),
            'valor_total': total
        }
