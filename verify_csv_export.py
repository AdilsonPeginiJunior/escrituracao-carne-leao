
import os
import csv
from models.receita_saude import ReceitaSaudeManager

def verify_csv_export():
    manager = ReceitaSaudeManager()
    
    # Case 1: With Beneficiary CPF
    manager.add_receita({
        'data': '01/01/2023',
        'valor': '100,00',
        'descricao': 'Test 1',
        'cpf_pagador': '111.111.111-11',
        'cpf_benef': '222.222.222-22',
        'cpf_prof': '999.999.999-99',
        'inscricao': 'CRP-12345'
    })
    
    # Case 2: Without Beneficiary CPF (should use Pagador)
    manager.add_receita({
        'data': '02/01/2023',
        'valor': '200,00',
        'descricao': 'Test 2',
        'cpf_pagador': '333.333.333-33',
        'cpf_benef': '',
        'cpf_prof': '888.888.888-88',
        'inscricao': 'CRP-67890'
    })
    
    output_file = 'verify_export.csv'
    if os.path.exists(output_file):
        os.remove(output_file)
        
    try:
        manager.export_csv(output_file)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
            
            # Row 1 (Case 1)
            row1 = rows[0]
            # Column 8 (index 7) should be Pagador
            assert row1[7] == '111.111.111-11', f"Row 1 Col 8 expected 111... got {row1[7]}"
            # Column 9 (index 8) should be Beneficiary
            assert row1[8] == '222.222.222-22', f"Row 1 Col 9 expected 222... got {row1[8]}"
            # Column 15 (index 14) should be cpf_prof
            assert row1[14] == '999.999.999-99', f"Row 1 Col 15 expected 999... got {row1[14]}"
            # Column 16 (index 15) should be inscricao
            assert row1[15] == 'CRP-12345', f"Row 1 Col 16 expected CRP-12345 got {row1[15]}"
            
            # Row 2 (Case 2)
            row2 = rows[1]
            # Column 8 (index 7) should be Pagador
            assert row2[7] == '333.333.333-33', f"Row 2 Col 8 expected 333... got {row2[7]}"
            # Column 9 (index 8) should be Pagador (because Benef is empty)
            assert row2[8] == '333.333.333-33', f"Row 2 Col 9 expected 333... got {row2[8]}"
             # Column 15 (index 14) should be cpf_prof
            assert row2[14] == '888.888.888-88', f"Row 2 Col 15 expected 888... got {row2[14]}"
            # Column 16 (index 15) should be inscricao
            assert row2[15] == 'CRP-67890', f"Row 2 Col 16 expected CRP-67890 got {row2[15]}"
            
            print("CSV Export Verification: PASSED")
            
    except Exception as e:
        print(f"CSV Export Verification: FAILED - {e}")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == "__main__":
    verify_csv_export()
