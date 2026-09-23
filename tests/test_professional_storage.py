import os
import tempfile
import unittest
from contextlib import contextmanager
from datetime import datetime
import json

from models.report_generator import ReportDataExtractor
from models.storage import (
    RecibosStorage,
    get_profissional_storage_dir,
    migrate_legacy_profissional_files,
    sanitize_profissional_name,
)


@contextmanager
def isolated_cwd(path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class ProfessionalStoragePathsTests(unittest.TestCase):
    def test_sanitize_profissional_name_removes_spaces_and_special_chars(self):
        self.assertEqual(sanitize_profissional_name("Ana Paula"), "AnaPaula")
        self.assertEqual(sanitize_profissional_name("João da Silva"), "JoaodaSilva")

    def test_get_profissional_storage_dir_uses_profissionais_folder(self):
        folder = get_profissional_storage_dir({"apelido": "Ana Paula"})
        self.assertTrue(folder.endswith(os.path.join("profissionais", "AnaPaula")))

    def test_migrate_legacy_files_to_profissional_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with isolated_cwd(tmpdir):
                with open("AnaPaula_pacientes.json", "w", encoding="utf-8") as f:
                    f.write('{"pacientes": []}')
                with open("AnaPaula_despesas_profissionais.json", "w", encoding="utf-8") as f:
                    f.write('{"despesas": []}')
                with open("AnaPaula_recibos_saude.json", "w", encoding="utf-8") as f:
                    f.write('{"recibos": []}')

                folder = migrate_legacy_profissional_files({"apelido": "Ana Paula"})

                self.assertTrue(os.path.exists(os.path.join(folder, "pacientes.json")))
                self.assertTrue(os.path.exists(os.path.join(folder, "despesas_profissionais.json")))
                self.assertTrue(os.path.exists(os.path.join(folder, "recibos_saude.json")))
                self.assertFalse(os.path.exists("AnaPaula_pacientes.json"))
                self.assertFalse(os.path.exists("AnaPaula_despesas_profissionais.json"))
                self.assertFalse(os.path.exists("AnaPaula_recibos_saude.json"))

    def test_clear_all_recibos_empties_storage_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "recibos_saude.json")
            storage = RecibosStorage(path)
            storage.save_recibo({"data": "01/01/2026"})

            storage.clear_all()

            with open(path, "r", encoding="utf-8") as file:
                self.assertEqual(json.load(file), {"recibos": []})


class ReportPatientCpfTests(unittest.TestCase):
    def test_report_formats_beneficiary_cpf(self):
        variables = ReportDataExtractor.extract_report_variables(
            {
                "cpf_pagador": "11111111111",
                "cpf_benef": "22222222222",
                "descricao": "",
            },
            {"nome_benef": "Paciente", "inicio": "", "fim": ""},
        )

        self.assertEqual(variables["#CPF"], "222.222.222-22")

    def test_report_formats_payer_cpf_when_beneficiary_is_same(self):
        variables = ReportDataExtractor.extract_report_variables(
            {
                "cpf_pagador": "333.333.333-33",
                "cpf_benef": "33333333333",
                "descricao": "",
            },
            {"nome_pagador": "Paciente", "inicio": "", "fim": ""},
        )

        self.assertEqual(variables["#CPF"], "333.333.333-33")

    def test_report_keeps_all_session_dates(self):
        variables = ReportDataExtractor.extract_report_variables(
            {
                "cpf_pagador": "11111111111",
                "cpf_benef": "11111111111",
                "descricao": (
                    "Referente a 04 sessões realizadas nos dias "
                    "01/01/2026, 08/01/2026, 15/01/2026 e 22/01/2026."
                ),
            },
            {"nome_pagador": "Paciente", "inicio": "", "fim": ""},
        )

        self.assertEqual(
            variables["#DataDasCons"],
            "01/01/2026, 08/01/2026, 15/01/2026 e 22/01/2026",
        )

    def test_report_keeps_all_dates_when_one_session_is_future(self):
        variables = ReportDataExtractor.extract_report_variables(
            {
                "cpf_pagador": "11111111111",
                "cpf_benef": "11111111111",
                "descricao": (
                    "Referente a 04 sessões realizadas nos dias "
                    "01/01/2026, 08/01/2026, 15/01/2026 e 01/01/2099."
                ),
            },
            {"nome_pagador": "Paciente", "inicio": "", "fim": ""},
        )

        self.assertEqual(
            variables["#DataDasCons"],
            "01/01/2026, 08/01/2026, 15/01/2026 e 01/01/2099",
        )

    def test_report_uses_current_date_for_signature(self):
        variables = ReportDataExtractor.extract_report_variables(
            {
                "cpf_pagador": "11111111111",
                "cpf_benef": "11111111111",
                "descricao": "Referente a 01 sessão no dia 01/01/2020.",
            },
            {"nome_pagador": "Paciente", "inicio": "", "fim": ""},
        )
        hoje = datetime.now().date()
        mes = ReportDataExtractor.MESES_EXTENSO[hoje.month]

        self.assertEqual(
            variables["#DataAssinatura"],
            f"{hoje.day} de {mes} de {hoje.year}",
        )


if __name__ == "__main__":
    unittest.main()
