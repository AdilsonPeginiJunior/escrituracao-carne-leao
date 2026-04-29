
import csv
import os
import json
from models.despesas import DespesasManager


def verify_despesas_export():
    manager = DespesasManager()

    # Test P10.01.00004 with Multa and Juros (special case)
    test_code = 'P10.01.00004'  # Contribuições obrigatórias
    test_desc = 'Pagamento de Contribuições obrigatórias a entidades de classe'

    print(f"Testing with: {test_code} - {test_desc}")

    manager.add_despesa({
        'data': '20/06/2026',
        'codigo': test_code,
        'valor': '500,00',
        'descricao': test_desc,
        'multa': '10,00',
        'juros': '5,00',
        'competencia': '05/2026'
    })

    output_file = 'verify_despesas_export_v2.csv'
    if os.path.exists(output_file):
        os.remove(output_file)

    try:
        manager.export_csv(output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

            if not rows:
                print("FAILED: CSV empty")
                return

            row1 = rows[0]
            # Column 2 (index 1) is Code
            assert row1[1] == test_code, f"Expected code {test_code}, got {row1[1]}"
            # Column 5 (index 4) is Multa
            assert row1[4] == '10,00', f"Expected multa 10,00, got {row1[4]}"
            # Column 6 (index 5) is Juros
            assert row1[5] == '5,00', f"Expected juros 5,00, got {row1[5]}"
            # Column 7 (index 6) is Competence
            assert row1[6] == '05/2026', f"Expected competence 05/2026, got {row1[6]}"

            print("Despesas Export Verification V2 (P10.01.00004 with Multa/Juros): PASSED")

    except Exception as e:
        print(f"Despesas Export Verification FAILED - {e}")

    # Test P11.01.00006 exports with only the basic fields
    manager.clear()
    test_code = 'P11.01.00006'
    test_desc = 'Pagamento de Carnê-leão pago'
    manager.add_despesa({
        'data': '20/06/2026',
        'codigo': test_code,
        'valor': '500,00',
        'descricao': test_desc,
        'multa': '0',
        'juros': '0',
        'competencia': '06/2026'
    })

    output_file = 'verify_despesas_export_p11.csv'
    if os.path.exists(output_file):
        os.remove(output_file)

    try:
        manager.export_csv(output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

            if not rows:
                print("FAILED: CSV empty for P11.01.00006")
                return

            row1 = rows[0]
            assert len(
                row1) == 4, f"Expected 4 columns for P11.01.00006, got {len(row1)}"
            assert row1[1] == test_code, f"Expected code {test_code}, got {row1[1]}"
            assert row1[2] == '500,00', f"Expected valor 500,00, got {row1[2]}"
            assert row1[3] == test_desc, f"Expected descricao {test_desc}, got {row1[3]}"

            print("Despesas Export Verification V2 (P11.01.00006): PASSED")

    except Exception as e:
        print(f"Despesas Export Verification FAILED - P11.01.00006: {e}")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


    # Test P10 exports with only the basic fields (no competencia, multa, juros)
    manager.clear()
    test_code = 'P10.01.00013'
    test_desc = 'Pagamento de Remuneração paga a terceiros, com vínculo empregatício, INSS e FGTS'
    manager.add_despesa({
        'data': '20/06/2026',
        'codigo': test_code,
        'valor': '100,00',
        'descricao': test_desc,
        'multa': '10,00',
        'juros': '5,00',
        'competencia': '06/2026'
    })

    output_file = 'verify_despesas_export_p10.csv'
    if os.path.exists(output_file):
        os.remove(output_file)

    try:
        manager.export_csv(output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

            if not rows:
                print("FAILED: CSV empty for P10.01.00013")
                return

            row1 = rows[0]
            assert len(row1) == 4, f"Expected 4 columns for P10.01.00013, got {len(row1)}"
            assert row1[1] == test_code, f"Expected code {test_code}, got {row1[1]}"
            assert row1[2] == '100,00', f"Expected valor 100,00, got {row1[2]}"
            assert row1[3] == test_desc, f"Expected descricao {test_desc}, got {row1[3]}"

            print("Despesas Export Verification V2 (P10.01.00013): PASSED")

    except Exception as e:
        print(f"Despesas Export Verification FAILED - P10.01.00013: {e}")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


if __name__ == "__main__":
    verify_despesas_export()
