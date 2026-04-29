import json
import os
from typing import List, Dict
from datetime import datetime


class RecibosStorage:
    """Gerencia o armazenamento de recibos em arquivo JSON"""

    def __init__(self, file_path: str = "recibos_saude.json"):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Cria o arquivo se não existir"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"recibos": []}, f, ensure_ascii=False, indent=2)

    def load_recibos(self) -> List[Dict]:
        """Carrega todos os recibos"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("recibos", [])
        except Exception as e:
            print(f"Erro ao carregar recibos: {e}")
            return []

    def save_recibo(self, recibo: Dict) -> int:
        """Salva um novo recibo e retorna seu ID"""
        recibos = self.load_recibos()

        # Gerar ID baseado no timestamp
        recibo_id = int(datetime.now().timestamp() * 1000)
        recibo['id'] = recibo_id
        recibo['data_criacao'] = datetime.now().isoformat()

        recibos.append(recibo)
        self._save_all(recibos)

        return recibo_id

    def update_recibo(self, recibo_id: int, recibo_data: Dict) -> bool:
        """Atualiza um recibo existente"""
        recibos = self.load_recibos()

        for i, r in enumerate(recibos):
            if r.get('id') == recibo_id:
                recibo_data['id'] = recibo_id
                recibo_data['data_criacao'] = r.get('data_criacao')
                recibo_data['data_atualizacao'] = datetime.now().isoformat()
                recibos[i] = recibo_data
                self._save_all(recibos)
                return True

        return False

    def delete_recibo(self, recibo_id: int) -> bool:
        """Deleta um recibo"""
        recibos = self.load_recibos()
        recibos = [r for r in recibos if r.get('id') != recibo_id]
        self._save_all(recibos)
        return True

    def get_recibo(self, recibo_id: int) -> Dict:
        """Obtém um recibo específico"""
        recibos = self.load_recibos()
        for r in recibos:
            if r.get('id') == recibo_id:
                return r
        return None

    def _save_all(self, recibos: List[Dict]):
        """Salva todos os recibos no arquivo"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump({"recibos": recibos}, f, ensure_ascii=False, indent=2)

    def clear_all(self):
        """Limpa todos os recibos"""
        self._save_all([])


class DespesasStorage:
    """Gerencia o armazenamento de despesas em arquivo JSON"""

    def __init__(self, file_path: str = "despesas_profissionais.json"):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Cria o arquivo se não existir"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"despesas": []}, f, ensure_ascii=False, indent=2)

    def load_despesas(self) -> List[Dict]:
        """Carrega todas as despesas"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("despesas", [])
        except Exception as e:
            print(f"Erro ao carregar despesas: {e}")
            return []

    def save_despesa(self, despesa: Dict) -> int:
        """Salva uma nova despesa e retorna seu ID"""
        despesas = self.load_despesas()

        # Gerar ID baseado no timestamp
        despesa_id = int(datetime.now().timestamp() * 1000)
        despesa['id'] = despesa_id
        despesa['data_criacao'] = datetime.now().isoformat()

        despesas.append(despesa)
        self._save_all(despesas)

        return despesa_id

    def update_despesa(self, despesa_id: int, despesa_data: Dict) -> bool:
        """Atualiza uma despesa existente"""
        despesas = self.load_despesas()

        for i, d in enumerate(despesas):
            if d.get('id') == despesa_id:
                despesa_data['id'] = despesa_id
                despesa_data['data_criacao'] = d.get('data_criacao')
                despesa_data['data_atualizacao'] = datetime.now().isoformat()
                despesas[i] = despesa_data
                self._save_all(despesas)
                return True

        return False

    def delete_despesa(self, despesa_id: int) -> bool:
        """Deleta uma despesa"""
        despesas = self.load_despesas()
        despesas = [d for d in despesas if d.get('id') != despesa_id]
        self._save_all(despesas)
        return True

    def get_despesa(self, despesa_id: int) -> Dict:
        """Obtém uma despesa específica"""
        despesas = self.load_despesas()
        for d in despesas:
            if d.get('id') == despesa_id:
                return d
        return None

    def _save_all(self, despesas: List[Dict]):
        """Salva todas as despesas no arquivo"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump({"despesas": despesas}, f, ensure_ascii=False, indent=2)

    def clear_all(self):
        """Limpa todas as despesas"""
        self._save_all([])


class ProfissionaisStorage:
    """Gerencia o armazenamento de profissionais em arquivo JSON"""

    def __init__(self, file_path: str = "profissionais.json"):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Cria o arquivo se não existir"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"profissionais": []}, f,
                          ensure_ascii=False, indent=2)

    def load_profissionais(self) -> List[Dict]:
        """Carrega todos os profissionais"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("profissionais", [])
        except Exception as e:
            print(f"Erro ao carregar profissionais: {e}")
            return []

    def save_profissional(self, profissional: Dict) -> int:
        """Salva um novo profissional e retorna seu ID"""
        profissionais = self.load_profissionais()

        # Gerar ID baseado no timestamp
        prof_id = int(datetime.now().timestamp() * 1000)
        profissional['id'] = prof_id
        profissional['data_criacao'] = datetime.now().isoformat()

        profissionais.append(profissional)
        self._save_all(profissionais)

        return prof_id

    def update_profissional(self, prof_id: int, prof_data: Dict) -> bool:
        """Atualiza um profissional existente"""
        profissionais = self.load_profissionais()

        for i, p in enumerate(profissionais):
            if p.get('id') == prof_id:
                prof_data['id'] = prof_id
                prof_data['data_criacao'] = p.get('data_criacao')
                prof_data['data_atualizacao'] = datetime.now().isoformat()
                profissionais[i] = prof_data
                self._save_all(profissionais)
                return True

        return False

    def delete_profissional(self, prof_id: int) -> bool:
        """Deleta um profissional"""
        profissionais = self.load_profissionais()
        profissionais = [p for p in profissionais if p.get('id') != prof_id]
        self._save_all(profissionais)
        return True

    def get_profissional(self, prof_id: int) -> Dict:
        """Obtém um profissional específico"""
        profissionais = self.load_profissionais()
        for p in profissionais:
            if p.get('id') == prof_id:
                return p
        return None

    def get_profissional_by_cpf(self, cpf: str) -> Dict:
        """Obtém um profissional pelo CPF"""
        profissionais = self.load_profissionais()
        for p in profissionais:
            if p.get('cpf_prof') == cpf:
                return p
        return None

    def _save_all(self, profissionais: List[Dict]):
        """Salva todos os profissionais no arquivo"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump({"profissionais": profissionais},
                      f, ensure_ascii=False, indent=2)

    def clear_all(self):
        """Limpa todos os profissionais"""
        self._save_all([])


class PacientesStorage:
    """Gerencia o armazenamento de pacientes e beneficiários em arquivo JSON"""

    def __init__(self, file_path: str = "pacientes.json"):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Cria o arquivo se não existir"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"pacientes": []}, f, ensure_ascii=False, indent=2)

    def load_pacientes(self) -> List[Dict]:
        """Carrega todos os pacientes"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("pacientes", [])
        except Exception as e:
            print(f"Erro ao carregar pacientes: {e}")
            return []

    def save_paciente(self, paciente: Dict) -> int:
        """Salva um novo paciente e retorna seu ID"""
        pacientes = self.load_pacientes()

        # Gerar ID baseado no timestamp
        pac_id = int(datetime.now().timestamp() * 1000)
        paciente['id'] = pac_id
        paciente['data_criacao'] = datetime.now().isoformat()

        pacientes.append(paciente)
        self._save_all(pacientes)

        return pac_id

    def update_paciente(self, pac_id: int, pac_data: Dict) -> bool:
        """Atualiza um paciente existente"""
        pacientes = self.load_pacientes()

        for i, p in enumerate(pacientes):
            if p.get('id') == pac_id:
                pac_data['id'] = pac_id
                pac_data['data_criacao'] = p.get('data_criacao')
                pac_data['data_atualizacao'] = datetime.now().isoformat()
                pacientes[i] = pac_data
                self._save_all(pacientes)
                return True

        return False

    def delete_paciente(self, pac_id: int) -> bool:
        """Deleta um paciente"""
        pacientes = self.load_pacientes()
        pacientes = [p for p in pacientes if p.get('id') != pac_id]
        self._save_all(pacientes)
        return True

    def get_paciente(self, pac_id: int) -> Dict:
        """Obtém um paciente específico"""
        pacientes = self.load_pacientes()
        for p in pacientes:
            if p.get('id') == pac_id:
                return p
        return None

    def get_paciente_by_cpf(self, cpf: str) -> Dict:
        """Obtém um paciente pelo CPF"""
        pacientes = self.load_pacientes()
        for p in pacientes:
            if p.get('cpf_pagador') == cpf or p.get('cpf_benef') == cpf:
                return p
        return None

    def _save_all(self, pacientes: List[Dict]):
        """Salva todos os pacientes no arquivo"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump({"pacientes": pacientes}, f,
                      ensure_ascii=False, indent=2)

    def clear_all(self):
        """Limpa todos os pacientes"""
        self._save_all([])
