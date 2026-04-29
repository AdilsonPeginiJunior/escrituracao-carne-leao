import json
import os

class AuthManager:
    """Gerencia autenticação de profissionais"""
    
    def __init__(self, db_file="profissionais.json"):
        self.db_file = db_file
    
    def login(self, usuario, senha):
        """Verifica credenciais e retorna dados do profissional se válido"""
        try:
            if not os.path.exists(self.db_file):
                return None
                
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for prof in data.get('profissionais', []):
                if prof.get('usuario') == usuario and prof.get('senha') == senha:
                    return prof
            return None
        except Exception as e:
            print(f"Erro no login: {e}")
            return None
            
    def get_all_users(self):
        """Retorna lista de usuários para combobox de login"""
        try:
            if not os.path.exists(self.db_file):
                return []
                
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return [p.get('usuario') for p in data.get('profissionais', [])]
        except:
            return []
