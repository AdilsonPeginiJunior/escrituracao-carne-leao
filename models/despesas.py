import csv
from typing import List, Dict


class DespesasManager:
    """Gerenciador de despesas profissionais para Carnê Leão"""

    # Mapeamento de tipos de despesa e seus códigos
    CODIGO_DESPESAS = {
        'P20.01.00001': 'Previdência Oficial',
        'P20.01.00002': 'Pensão Alimentícia',
        'P20.01.00003': 'Imposto Pago no Exterior',
        'P20.01.00004': 'Imposto Pago',
        'P20.01.00005': 'Outras Despesas',
    }

    def __init__(self):
        self.despesas: List[Dict] = []

    def add_despesa(self, data: Dict) -> None:
        """Adiciona uma despesa à lista"""
        self.despesas.append(data)

    def clear(self) -> None:
        """Limpa todas as despesas"""
        self.despesas = []

    def export_csv(self, file_path: str) -> None:
        """
        Exporta as despesas para um arquivo CSV
        Formato compatível com Receita Federal.
        Para o código P11.01.00006, apenas os campos básicos são escritos.
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            # Escrever dados (SEM cabeçalho, conforme padrão da Receita Federal)
            for despesa in self.despesas:
                if despesa.get('codigo') == 'P11.01.00006':
                    row = [
                        despesa.get('data', ''),
                        despesa.get('codigo', 'P11.01.00006'),
                        despesa.get('valor', ''),
                        despesa.get('descricao', '')
                    ]
                else:
                    row = [
                        despesa.get('data', ''),
                        despesa.get('codigo', 'P20.01.00005'),
                        despesa.get('valor', ''),
                        despesa.get('descricao', ''),
                        despesa.get('multa', ''),
                        despesa.get('juros', ''),
                        despesa.get('competencia', '')
                    ]
                writer.writerow(row)

    def get_stats(self) -> Dict:
        """Retorna estatísticas das despesas"""
        total = sum(
            float(d.get('valor', '0').replace(',', '.'))
            for d in self.despesas
        )
        return {
            'total_despesas': len(self.despesas),
            'valor_total': total
        }
