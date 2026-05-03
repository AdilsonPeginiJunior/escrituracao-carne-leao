import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import csv
import json
from datetime import datetime
import os
from models.receita_saude import ReceitaSaudeManager
from models.despesas import DespesasManager
from models.storage import RecibosStorage, DespesasStorage, PacientesStorage
from models.auth import AuthManager
from ui.widgets import create_frame, create_label, create_entry, create_button, DatePickerFrame, MultiDatePickerFrame, MonthYearPickerFrame
from ui.relatorios import GerarRelatoriosWindow


class AplicacaoCarneLeao:
    # ... existing static methods ...

    def open_categorias_window(self):
        """Abre janela de gerenciamento de categorias"""
        from ui.categorias_despesas import CategoriaDespesaWindow
        window = CategoriaDespesaWindow(self.root)
        window.grab_set()
        window.focus_force()
        # Ao fechar, atualizar lista
        window.protocol("WM_DELETE_WINDOW",
                        lambda: self.on_categorias_window_close(window))

    def on_categorias_window_close(self, window):
        window.destroy()
        self.update_despesas_categorias()

    def update_despesas_categorias(self):
        """Atualiza a lista de categorias no combobox de despesas"""
        if not hasattr(self, 'despesas_entries') or "descricao" not in self.despesas_entries:
            return

        try:
            with open("categorias_despesas.json", "r", encoding="utf-8") as f:
                cats = json.load(f)

                # Garantir que todos tenham contagem_uso
                for c in cats:
                    if 'contagem_uso' not in c:
                        c['contagem_uso'] = 0

                # Separar P10, P11 e P20
                dedutiveis = [c for c in cats if c['codigo'].startswith('P10')]
                nao_dedutiveis = [
                    c for c in cats if c['codigo'].startswith('P11')]
                pagamentos = [c for c in cats if c['codigo'].startswith('P20')]
                outras = [c for c in cats if not c['codigo'].startswith(
                    'P10') and not c['codigo'].startswith('P11') and not c['codigo'].startswith('P20')]

                # Função de ordenação: Maior uso primeiro, depois alfabético
                def sort_key(x):
                    return (-x.get('contagem_uso', 0), x['descricao'])

                dedutiveis.sort(key=sort_key)
                nao_dedutiveis.sort(key=sort_key)
                pagamentos.sort(key=sort_key)
                outras.sort(key=sort_key)

                final_list = []

                if dedutiveis:
                    final_list.append("--- DESPESAS DEDUTÍVEIS (P10) ---")
                    final_list.extend([d['descricao'] for d in dedutiveis])

                if nao_dedutiveis:
                    if final_list:
                        final_list.append(
                            "--------------------------------------------------")
                    final_list.append("--- DESPESAS NÃO DEDUTÍVEIS (P11) ---")
                    final_list.extend([d['descricao'] for d in nao_dedutiveis])

                if pagamentos:
                    if final_list:
                        final_list.append(
                            "--------------------------------------------------")
                    final_list.append("--- PAGAMENTOS (P20) ---")
                    final_list.extend([d['descricao'] for d in pagamentos])

                if outras:
                    if final_list:
                        final_list.append(
                            "--------------------------------------------------")
                    final_list.append("--- OUTRAS ---")
                    final_list.extend([d['descricao'] for d in outras])

                self.despesas_entries["descricao"].configure(values=final_list)
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
            self.despesas_entries["descricao"].configure(values=[])

    @staticmethod
    def clean_cpf(cpf):
        """Remove caracteres não numéricos do CPF"""
        return "".join(filter(str.isdigit, str(cpf)))

    @staticmethod
    def format_cpf(cpf):
        """Formata CPF para 000.000.000-00"""
        cpf = AplicacaoCarneLeao.clean_cpf(cpf)
        if len(cpf) != 11:
            return cpf
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    @staticmethod
    def validate_cpf_checksum(cpf):
        """Valida os dígitos verificadores do CPF"""
        cpf = AplicacaoCarneLeao.clean_cpf(cpf)

        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        # Validação do primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[9]):
            return False

        # Validação do segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[10]):
            return False

        return True

    def __init__(self, root, current_user):
        self.root = root
        self.current_user = current_user

        self.root.title(
            f"Sistema - Carnê Leão | Profissional: {self.current_user.get('apelido', '')}")

        # Configurar caminho do arquivo de pacientes e de despesas baseado no profissional
        apelido_sanitizado = self.current_user.get(
            'apelido', 'default').replace(' ', '')
        # Ex: AnaPaula_pacientes.json / AnaPaula_despesas_profissionais.json
        self.pacientes_file = f"{apelido_sanitizado}_pacientes.json"
        self.despesas_file = f"{apelido_sanitizado}_despesas_profissionais.json"

        # Obter tamanho da tela e configurar janela com 90% do tamanho
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.85)

        # Posicionar a janela no centro da tela
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.root.geometry(
            f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Configurar redimensionamento dinâmico
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Gerenciadores
        self.receita_manager = ReceitaSaudeManager()
        self.despesas_manager = DespesasManager()
        self.recibos_storage = RecibosStorage()
        self.despesas_storage = DespesasStorage(self.despesas_file)
        self.pacientes_storage = PacientesStorage(self.pacientes_file)

        # Estado de edição
        self.editing_recibo_id = None
        self.editing_despesa_id = None

        # Configure cores
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.load_pacientes_data()

        self.setup_ui()

    def load_pacientes_data(self):
        """Carrega dados dos pacientes do arquivo JSON específico do profissional"""
        try:
            if os.path.exists(self.pacientes_file):
                with open(self.pacientes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pacientes = data.get('pacientes', [])
                    # Construir lista exibida de pagadores (mostrar nomes) e mapeamentos
                    displays = []
                    display_to_cpf = {}
                    pagador_to_benef = {}

                    for p in pacientes:
                        nome = p.get('nome_pagador') or p.get(
                            'nome_benef') or ''
                        cpf_pag_raw = p.get('cpf_pagador', '')
                        cpf_benef_raw = p.get('cpf_benef', '')

                        if not cpf_pag_raw:
                            continue

                        display = nome.strip() if nome else self.format_cpf(cpf_pag_raw)

                        # garantir valores únicos
                        if display not in displays:
                            displays.append(display)
                            display_to_cpf[display] = self.clean_cpf(
                                cpf_pag_raw)

                        # preparar lista de beneficiários para este display
                        cpf_benef = self.format_cpf(
                            cpf_benef_raw) if cpf_benef_raw else self.format_cpf(cpf_pag_raw)
                        if display not in pagador_to_benef:
                            pagador_to_benef[display] = set()
                        pagador_to_benef[display].add(cpf_benef)

                    # Ordenar listas
                    self.cpf_pagador_values = sorted(displays)
                    # Converter sets para listas ordenadas de beneficiários (CPFs formatados)
                    self.pagador_to_benef = {
                        k: sorted(list(v)) for k, v in pagador_to_benef.items()}
                    self.display_to_cpf = display_to_cpf
            else:
                self.cpf_pagador_values = []
                self.pagador_to_benef = {}
                # Criar arquivo vazio se não existir para o profissional
                if self.pacientes_file:
                    with open(self.pacientes_file, 'w', encoding='utf-8') as f:
                        json.dump({"pacientes": []}, f, indent=2)

        except Exception as e:
            print(f"Erro ao carregar pacientes: {e}")
            self.cpf_pagador_values = []
            self.pagador_to_benef = {}

    def setup_ui(self):
        # Frame principal com suporte a redimensionamento
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Título e Menu Superior
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            top_frame,
            text=f"Gerador de Arquivos CSV - Carnê Leão | {self.current_user.get('apelido', 'Usuário')}",
            font=("Arial", 20, "bold")
        )
        title.pack(side="left")

        # Botões de Menu
        menu_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        menu_frame.pack(side="right")

        ctk.CTkButton(menu_frame, text="Cad. Pacientes",
                      command=self.open_pacientes_window, width=120).pack(side="left", padx=5)
        # Apenas permitir cadastro de profissionais se desejar ou para todos?
        # O user pediu "No cadastro de profissionais...". Vou deixar botão visível.
        ctk.CTkButton(menu_frame, text="Cad. Profissionais",
                      command=self.open_profissionais_window, width=120).pack(side="left", padx=5)

        # Notebook (abas) com redimensionamento
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=10)

        # Aba Receita Saúde
        self.setup_receita_saude_tab()

        # Aba Despesas
        self.setup_despesas_tab()

    def open_pacientes_window(self):
        from ui.pacientes import CadastroPacientesWindow
        # Passar arquivo correto
        window = CadastroPacientesWindow(self.root, self.pacientes_file)
        window.grab_set()
        window.focus_force()
        # Opcional: callback para recarregar lista no form principal ao fechar
        window.protocol("WM_DELETE_WINDOW",
                        lambda: self.on_pacientes_window_close(window))

    def on_pacientes_window_close(self, window):
        window.destroy()
        self.load_pacientes_data()  # Recarregar dados para o combobox
        # Atualizar Combos
        self.cpf_pagador_cb.configure(values=self.cpf_pagador_values)
        self.cpf_benef_cb.set("")  # Resetar seleção para evitar inconsistência

    def open_profissionais_window(self):
        from ui.profissionais import CadastroProfissionaisWindow
        window = CadastroProfissionaisWindow(self.root)
        window.grab_set()
        window.focus_force()

    def open_relatorios_window(self):
        """Abre janela de geração de relatórios"""
        window = GerarRelatoriosWindow(self.root, self.current_user)
        window.grab_set()
        window.focus_force()

    def setup_receita_saude_tab(self):
        tab = self.notebook.add("Receita Saúde")

        # Container com dois painéis responsivo
        container = ctk.CTkFrame(tab)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)

        # Configurar grid da aba
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        # Painel esquerdo - Formulário (com scrollbar)
        left_frame = ctk.CTkFrame(container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            left_frame, text="Novo Recibo", font=("Arial", 14, "bold"))
        form_title.grid(row=0, column=0, pady=10, sticky="ew", padx=5)

        # Criar scrollbar para formulário
        form_canvas = tk.Canvas(left_frame, bg="#212121", highlightthickness=0)
        scrollbar = tk.Scrollbar(left_frame, command=form_canvas.yview)
        scrollable_frame = ctk.CTkFrame(form_canvas, fg_color="#212121")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: form_canvas.configure(
                scrollregion=form_canvas.bbox("all"))
        )

        form_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        form_canvas.configure(yscrollcommand=scrollbar.set)
        form_canvas.grid(row=1, column=0, sticky="nsew", padx=(5, 0))
        scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 5))

        # Usar scrollable_frame para adicionar campos
        form_frame = scrollable_frame
        # Campos fixos (automáticos do profissional logado)
        self.fixed_fields = {
            "codigo": "R01.001.001",
            "inscricao": self.current_user.get("inscricao", ""),
            "tipo_pagador": "PF",
            # Mantendo fixo ou deveria vir do cadastro? User disse que inscricao vem do profissional. Registro parece fixo no exemplo.
            "registro": "06/23007",
            "cpf_prof": self.current_user.get("cpf_prof", "")
        }

        # Apenas campos editáveis aparecem no formulário
        fields = [
            ("Data de Pagto (dd/mm/aaaa)", "data"),
            ("Valor (R$)", "valor")
        ]

        self.receita_entries = {}
        row_idx = 0
        for label_text, key in fields:
            label = ctk.CTkLabel(
                form_frame, text=label_text, font=("Arial", 10))
            label.grid(row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
            row_idx += 1

            if key == "data":
                widget = DatePickerFrame(form_frame)
                widget.grid(row=row_idx, column=0, pady=(
                    2, 8), padx=5, sticky="ew")
            else:
                widget = ctk.CTkEntry(form_frame, width=280)
                widget.grid(row=row_idx, column=0, pady=(
                    2, 8), padx=5, sticky="ew")

            self.receita_entries[key] = widget
            row_idx += 1

        # Campos de CPF (ComboBox)
        # CPF Pagador
        label = ctk.CTkLabel(
            form_frame, text="CPF Pagador", font=("Arial", 10))
        label.grid(row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1

        self.cpf_pagador_cb = ctk.CTkComboBox(
            form_frame,
            values=self.cpf_pagador_values,
            command=self.on_cpf_pagador_change,
            width=280
        )
        self.cpf_pagador_cb.grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        self.cpf_pagador_cb.set("")  # Iniciar vazio
        self.receita_entries["cpf_pagador"] = self.cpf_pagador_cb
        row_idx += 1

        # CPF Beneficiário
        label = ctk.CTkLabel(
            form_frame, text="CPF do Beneficiário", font=("Arial", 10))
        label.grid(row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1

        self.cpf_benef_cb = ctk.CTkComboBox(form_frame, values=[], width=280)
        self.cpf_benef_cb.grid(row=row_idx, column=0,
                               pady=(2, 8), padx=5, sticky="ew")
        self.cpf_benef_cb.set("")  # Iniciar vazio
        self.receita_entries["cpf_benef"] = self.cpf_benef_cb
        row_idx += 1

        # Adicionar widget de múltiplas datas para descrição
        desc_label = ctk.CTkLabel(
            form_frame, text="Descrição/Observações (Sessões)", font=("Arial", 10))
        desc_label.grid(row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1

        self.multi_date_picker = MultiDatePickerFrame(form_frame)
        self.multi_date_picker.grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        self.receita_entries["descricao"] = self.multi_date_picker
        row_idx += 1

        # Botões de ação
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=row_idx, column=0, pady=15, padx=5, sticky="ew")

        # Botão Novo Recibo
        self.new_recibo_btn = ctk.CTkButton(
            button_frame,
            text="Novo Recibo",
            command=self.clear_form_receita,
            fg_color="#1E88E5",  # Azul
            width=130
        )
        self.new_recibo_btn.pack(pady=5)

        self.save_recibo_btn = ctk.CTkButton(
            button_frame,
            text="Salvar Recibo",
            command=self.save_recibo_saude,
            fg_color="green",
            width=130
        )
        self.save_recibo_btn.pack(pady=5)

        clear_btn = ctk.CTkButton(
            button_frame,
            text="Limpar Formulário",
            command=self.clear_form_receita,
            width=130
        )
        clear_btn.pack(pady=5)

        # Painel direito - Lista de recibos
        right_frame = ctk.CTkFrame(container)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        list_title = ctk.CTkLabel(
            right_frame, text="Recibos Salvos", font=("Arial", 14, "bold"))
        list_title.grid(row=0, column=0, pady=10, sticky="nsew")

        # Frame com scrollbar para lista de recibos
        list_frame = ctk.CTkFrame(right_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Canvas com scrollbar
        self.recibos_canvas = tk.Canvas(
            list_frame, bg="#2a2a2a", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, command=self.recibos_canvas.yview)
        scrollable_frame = ctk.CTkFrame(
            self.recibos_canvas, fg_color="#2a2a2a")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.recibos_canvas.configure(
                scrollregion=self.recibos_canvas.bbox("all"))
        )

        self.recibos_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw")
        self.recibos_canvas.configure(yscrollcommand=scrollbar.set)

        self.recibos_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.recibos_frame = scrollable_frame

        # Botão para gerar CSV
        export_btn = ctk.CTkButton(
            right_frame,
            text="Exportar Recibos para CSV",
            command=self.export_recibos_csv,
            fg_color="darkgreen",
            height=40,
            font=("Arial", 12, "bold")
        )
        export_btn.grid(row=2, column=0, pady=10, sticky="ew", padx=10)

        # Botão para gerar relatórios
        relatorios_btn = ctk.CTkButton(
            right_frame,
            text="Gerar Relatórios",
            command=self.open_relatorios_window,
            fg_color="darkblue",
            height=40,
            font=("Arial", 12, "bold")
        )
        relatorios_btn.grid(row=3, column=0, pady=10, sticky="ew", padx=10)

        # Carregar recibos ao iniciar
        self.refresh_recibos_list()

    def setup_despesas_tab(self):
        tab = self.notebook.add("Despesas Profissionais")

        # Container com dois painéis
        container = ctk.CTkFrame(tab)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configurar grid responsivo
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=0)  # Esquerda (Form)
        container.columnconfigure(1, weight=1)  # Direita (Lista)

        # Configurar grid da aba
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        # Painel esquerdo - Formulário com Canvas scrollável
        # Aumentando largura do painel esquerdo ou ajustando inputs
        left_frame = ctk.CTkFrame(container, width=350)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.grid_propagate(False)  # Forçar largura

        form_title = ctk.CTkLabel(
            left_frame, text="Nova Despesa", font=("Arial", 14, "bold"))
        form_title.grid(row=0, column=0, pady=10, sticky="ew", padx=5)

        # Botão para gerenciar categorias
        btn_cat = ctk.CTkButton(left_frame, text="Gerenciar Categorias", height=24,
                                command=self.open_categorias_window, font=("Arial", 10))
        # Overlay ou abaixo do título
        btn_cat.grid(row=0, column=0, pady=(40, 0), sticky="n")

        # Canvas com scrollbar para o formulário
        form_canvas = tk.Canvas(
            left_frame, bg="#2a2a2a", highlightthickness=0, height=400, width=300)
        form_scrollbar = tk.Scrollbar(
            left_frame, command=form_canvas.yview)
        form_frame = ctk.CTkFrame(form_canvas, fg_color="#2a2a2a")

        form_frame.bind(
            "<Configure>",
            lambda e: form_canvas.configure(
                scrollregion=form_canvas.bbox("all"))
        )

        # Width fixo para alinhar
        form_canvas.create_window(
            (0, 0), window=form_frame, anchor="nw", width=300)
        form_canvas.configure(yscrollcommand=form_scrollbar.set)

        form_canvas.grid(row=1, column=0, sticky="nsew", padx=(5, 0))
        form_scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 5))
        left_frame.rowconfigure(1, weight=1)

        # Campos
        self.despesas_entries = {}
        row_idx = 0

        # 1. Data de Pagto (Calendário)
        ctk.CTkLabel(form_frame, text="Data de Pagto", font=("Arial", 10)).grid(
            row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1

        self.despesas_entries["data"] = DatePickerFrame(form_frame)
        self.despesas_entries["data"].grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        row_idx += 1

        # 2. Descrição (Combobox com categorias)
        ctk.CTkLabel(form_frame, text="Descrição", font=("Arial", 10)).grid(
            row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1

        self.despesas_entries["descricao"] = ctk.CTkComboBox(
            form_frame, width=240)
        self.despesas_entries["descricao"].grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        # Popular combobox
        self.update_despesas_categorias()
        row_idx += 1

        # 3. Valor
        ctk.CTkLabel(form_frame, text="Valor (R$)", font=("Arial", 10)).grid(
            row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1

        self.despesas_entries["valor"] = ctk.CTkEntry(form_frame, width=240)
        self.despesas_entries["valor"].grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        row_idx += 1

        # 4. Competência (Mês/Ano Picker)
        ctk.CTkLabel(form_frame, text="Competência (mm/aaaa)", font=("Arial", 10)
                     ).grid(row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1

        self.despesas_entries["competencia"] = MonthYearPickerFrame(form_frame)
        self.despesas_entries["competencia"].grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        row_idx += 1

        # 5. Valor da Multa (Opcional)
        ctk.CTkLabel(form_frame, text="Valor da Multa (R$)", font=("Arial", 10)).grid(
            row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1
        self.despesas_entries["multa"] = ctk.CTkEntry(
            form_frame, width=240, placeholder_text="Opcional")
        self.despesas_entries["multa"].grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        row_idx += 1

        # 6. Valor dos Juros (Opcional)
        ctk.CTkLabel(form_frame, text="Valor dos Juros (R$)", font=("Arial", 10)).grid(
            row=row_idx, column=0, pady=(8, 2), padx=5, sticky="w")
        row_idx += 1
        self.despesas_entries["juros"] = ctk.CTkEntry(
            form_frame, width=240, placeholder_text="Opcional")
        self.despesas_entries["juros"].grid(
            row=row_idx, column=0, pady=(2, 8), padx=5, sticky="ew")
        row_idx += 1

        # Botões de ação em linha
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row_idx, column=0, pady=20, padx=5, sticky="ew")

        self.save_despesa_btn = ctk.CTkButton(
            button_frame,
            text="Salvar",
            command=self.save_despesa,
            fg_color="green",
            width=130
        )
        self.save_despesa_btn.pack(side="left", padx=5, expand=True)

        new_btn = ctk.CTkButton(
            button_frame,
            text="Novo",
            command=self.clear_form_despesa,
            width=130
        )
        new_btn.pack(side="left", padx=5, expand=True)

        # Painel direito - Lista de despesas
        right_frame = ctk.CTkFrame(container)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        list_title = ctk.CTkLabel(
            right_frame, text="Despesas Salvas", font=("Arial", 14, "bold"))
        list_title.grid(row=0, column=0, pady=10, sticky="ew", padx=10)

        # Frame com scrollbar para lista de despesas
        list_frame = ctk.CTkFrame(right_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Canvas com scrollbar
        self.despesas_canvas = tk.Canvas(
            list_frame, bg="#2a2a2a", highlightthickness=0)
        scrollbar = tk.Scrollbar(
            list_frame, command=self.despesas_canvas.yview)
        scrollable_frame = ctk.CTkFrame(
            self.despesas_canvas, fg_color="#2a2a2a")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.despesas_canvas.configure(
                scrollregion=self.despesas_canvas.bbox("all"))
        )

        self.despesas_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw")
        self.despesas_canvas.configure(yscrollcommand=scrollbar.set)

        self.despesas_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.despesas_frame = scrollable_frame

        # Botão para gerar CSV
        export_btn = ctk.CTkButton(
            right_frame,
            text="Exportar Despesas para CSV",
            command=self.export_despesas_csv,
            fg_color="darkgreen",
            height=40,
            font=("Arial", 12, "bold")
        )
        export_btn.grid(row=2, column=0, pady=10, sticky="ew", padx=10)

        # Carregar despesas ao iniciar
        self.refresh_despesas_list()

    def save_recibo_saude(self):
        """Salva um novo recibo ou atualiza um existente"""
        try:
            # Resetar bordas
            for widget in self.receita_entries.values():
                if hasattr(widget, 'configure'):
                    try:
                        # Cores padrão do ctk
                        widget.configure(border_color=["#979da2", "#565b5e"])
                    except:
                        pass  # Widget pode não ter border_color

            data = {}
            has_error = False
            first_error_widget = None

            for key, entry in self.receita_entries.items():
                value = entry.get().strip()

                # Se o combobox de pagador estiver mostrando o nome do paciente,
                # mapear para o CPF real antes de validar
                if key == 'cpf_pagador' and hasattr(self, 'display_to_cpf') and value in self.display_to_cpf:
                    value = self.display_to_cpf[value]

                # Validação de campos obrigatórios
                if key in ["data", "valor", "cpf_pagador", "cpf_benef"] and not value:
                    if hasattr(entry, 'configure'):
                        entry.configure(border_color="red")
                    has_error = True
                    if not first_error_widget:
                        first_error_widget = entry

                # Validação de CPF
                if key in ["cpf_pagador", "cpf_benef"] and value:
                    if not self.validate_cpf_checksum(value):
                        if hasattr(entry, 'configure'):
                            entry.configure(border_color="red")
                        has_error = True
                        if not first_error_widget:
                            first_error_widget = entry
                        messagebox.showerror(
                            "Erro de Validação", f"CPF inválido no campo: {key.replace('_', ' ').title()}")
                        return  # Retorna imediatamente no primeiro erro de CPF para não spamar

                data[key] = value

            # Limpar CPFs antes de salvar (remover formatação)
            if "cpf_pagador" in data:
                data["cpf_pagador"] = self.clean_cpf(data["cpf_pagador"])
            if "cpf_benef" in data:
                data["cpf_benef"] = self.clean_cpf(data["cpf_benef"])

            if has_error:
                messagebox.showerror(
                    "Erro", "Preencha todos os campos obrigatórios corretamente!")
                return

            # Adicionar valores fixos
            data.update(self.fixed_fields)

            # Validar formato de data
            try:
                datetime.strptime(data["data"], "%d/%m/%Y")
            except ValueError:
                self.receita_entries["data"].date_entry.configure(
                    border_color="red")
                messagebox.showerror(
                    "Erro", "Data deve estar no formato dd/mm/aaaa")
                return

            # Validar valor
            try:
                float(data["valor"].replace(",", "."))
            except ValueError:
                self.receita_entries["valor"].configure(border_color="red")
                messagebox.showerror("Erro", "Valor deve ser um número válido")
                return

            if self.editing_recibo_id:
                # Atualizar
                self.recibos_storage.update_recibo(
                    self.editing_recibo_id, data)
                messagebox.showinfo(
                    "Sucesso", "Recibo atualizado com sucesso!")
                self.editing_recibo_id = None
                self.save_recibo_btn.configure(text="Salvar Recibo")
            else:
                # Salvar novo
                self.recibos_storage.save_recibo(data)
                messagebox.showinfo("Sucesso", "Recibo salvo com sucesso!")

            self.clear_form_receita()
            self.refresh_recibos_list()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar recibo: {str(e)}")

    def on_cpf_pagador_change(self, choice):
        """Callback quando o CPF Pagador é alterado"""
        benefs = self.pagador_to_benef.get(choice, [])
        self.cpf_benef_cb.configure(values=benefs)

        if benefs:
            self.cpf_benef_cb.set(benefs[0])
        else:
            self.cpf_benef_cb.set(choice)

    def save_despesa(self):
        """Salva uma nova despesa ou atualiza uma existente"""
        try:
            data = {}
            # Campos obrigatórios: data, valor, descricao, competencia
            for key in ["data", "valor", "descricao", "competencia"]:
                if key in self.despesas_entries:
                    value = self.despesas_entries[key].get().strip()
                    if not value:
                        messagebox.showerror(
                            "Erro", f"Campo '{key}' é obrigatório!")
                        return
                    data[key] = value

            # Campos opcionais
            for key in ["multa", "juros"]:
                if key in self.despesas_entries:
                    value = self.despesas_entries[key].get().strip()
                    if value:
                        # Validar se é número
                        try:
                            float(value.replace(",", "."))
                            data[key] = value
                        except ValueError:
                            messagebox.showerror(
                                "Erro", f"Campo '{key}' deve ser um número válido!")
                            return
                    else:
                        data[key] = ""

            # Buscar código baseado na descrição e incrementar uso
            try:
                with open("categorias_despesas.json", "r+", encoding="utf-8") as f:
                    cats = json.load(f)

                    # Validar se o usuário selecionou um separador
                    if "---" in data["descricao"]:
                        messagebox.showwarning(
                            "Aviso", "Selecione uma despesa válida, não o separador.")
                        return

                    target_cat = next(
                        (c for c in cats if c["descricao"] == data["descricao"]), None)

                    if not target_cat:
                        messagebox.showerror(
                            "Erro", "Descrição inválida ou não encontrada na lista!")
                        return

                    data["codigo"] = target_cat["codigo"]

                    # Incrementar uso
                    target_cat['contagem_uso'] = target_cat.get(
                        'contagem_uso', 0) + 1

                    # Salvar arquivo atualizado (seek 0 para sobrescrever)
                    f.seek(0)
                    json.dump(cats, f, indent=4, ensure_ascii=False)
                    f.truncate()

                    # Atualizar lista na UI para refletir nova ordenação na próxima vez
                    # Mas só se não estiver no meio de edições complexas?
                    # Melhor atualizar para garantir consistencia
                    # self.update_despesas_categorias() -> Pode resetar a seleção se fizermos agora. Melhor não.

            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Erro ao buscar código da despesa: {e}")
                return

            # Validar formato de data
            try:
                datetime.strptime(data["data"], "%d/%m/%Y")
            except ValueError:
                messagebox.showerror(
                    "Erro", "Data deve estar no formato dd/mm/aaaa")
                return

            # Validar valor
            try:
                float(data["valor"].replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor deve ser um número válido")
                return

            if self.editing_despesa_id:
                # Atualizar
                self.despesas_storage.update_despesa(
                    self.editing_despesa_id, data)
                messagebox.showinfo(
                    "Sucesso", "Despesa atualizada com sucesso!")
                self.editing_despesa_id = None
                self.save_despesa_btn.configure(
                    text="Salvar")  # Resetar texto do botão
            else:
                # Salvar nova
                self.despesas_storage.save_despesa(data)
                messagebox.showinfo("Sucesso", "Despesa salva com sucesso!")

            self.clear_form_despesa()
            self.refresh_despesas_list()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar despesa: {str(e)}")

    def edit_recibo(self, recibo_id):
        """Carrega um recibo para edição"""
        recibo = self.recibos_storage.get_recibo(recibo_id)
        if not recibo:
            return

        self.editing_recibo_id = recibo_id
        self.save_recibo_btn.configure(text="Atualizar Recibo")

        for key, entry in self.receita_entries.items():
            if key in recibo:
                value = recibo[key]

                # Formatar CPF para exibição se for um campo de CPF
                if key in ["cpf_pagador", "cpf_benef"]:
                    value = self.format_cpf(value)

                if isinstance(entry, ctk.CTkEntry):
                    entry.delete(0, "end")
                    entry.insert(0, value)
                elif isinstance(entry, ctk.CTkComboBox):
                    entry.set(value)
                elif hasattr(entry, 'delete'):
                    entry.delete(0, "end")
                    entry.insert(0, value)

    def delete_recibo(self, recibo_id):
        """Deleta um recibo"""
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este recibo?"):
            self.recibos_storage.delete_recibo(recibo_id)
            self.refresh_recibos_list()
            messagebox.showinfo("Sucesso", "Recibo deletado com sucesso!")

    def edit_despesa(self, despesa_id):
        """Carrega uma despesa para edição"""
        despesa = self.despesas_storage.get_despesa(despesa_id)
        if not despesa:
            return

        self.editing_despesa_id = despesa_id
        self.save_despesa_btn.configure(text="Atualizar")

        # Limpar form antes de carregar
        self.clear_form_despesa(reset_id=False)

        for key, entry in self.despesas_entries.items():
            if key in despesa:
                value = despesa[key]
                if key == "competencia" and hasattr(entry, 'set'):
                    entry.set(value)
                elif isinstance(entry, ctk.CTkEntry):
                    entry.delete(0, "end")
                    entry.insert(0, value)
                elif isinstance(entry, ctk.CTkComboBox):
                    entry.set(value)
                elif hasattr(entry, 'delete'):
                    entry.delete(0, "end")
                    entry.insert(0, value)

    def delete_despesa(self, despesa_id):
        """Deleta uma despesa"""
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar esta despesa?"):
            self.despesas_storage.delete_despesa(despesa_id)
            self.refresh_despesas_list()
            messagebox.showinfo("Sucesso", "Despesa deletada com sucesso!")

    def clear_form_despesa(self, reset_id=True):
        """Limpa todos os campos da despesa"""
        for key, entry in self.despesas_entries.items():
            if hasattr(entry, 'delete') and not isinstance(entry, ctk.CTkComboBox):
                try:
                    entry.delete(0, "end")
                except:
                    pass
            elif isinstance(entry, ctk.CTkComboBox):
                entry.set("")

            # Resetar MonthYearPicker se tiver método específico ou deixar como está
            # Se for data, limpar
            if key == "data" and hasattr(entry, 'delete'):
                entry.delete(0, "end")

        if reset_id:
            self.editing_despesa_id = None
            self.save_despesa_btn.configure(text="Salvar")

    def refresh_recibos_list(self):
        """Atualiza a lista de recibos exibida"""
        # Limpar frame
        for widget in self.recibos_frame.winfo_children():
            widget.destroy()

        recibos = self.recibos_storage.load_recibos()

        if not recibos:
            label = ctk.CTkLabel(
                self.recibos_frame,
                text="Nenhum recibo salvo",
                text_color="gray"
            )
            label.pack(pady=20)
            return

        for recibo in recibos:
            self.create_recibo_item(recibo)

    def refresh_despesas_list(self):
        """Atualiza a lista de despesas exibida"""
        # Limpar frame
        for widget in self.despesas_frame.winfo_children():
            widget.destroy()

        despesas = self.despesas_storage.load_despesas()

        if not despesas:
            label = ctk.CTkLabel(
                self.despesas_frame,
                text="Nenhuma despesa salva",
                text_color="gray"
            )
            label.pack(pady=20)
            return

        for despesa in despesas:
            self.create_despesa_item(despesa)

    def create_recibo_item(self, recibo):
        """Cria um item de recibo na lista"""
        item_frame = ctk.CTkFrame(
            self.recibos_frame, fg_color="#3a3a3a", corner_radius=8)
        item_frame.pack(fill="x", padx=5, pady=5)

        # Info do recibo
        info_text = f"Data: {recibo.get('data', 'N/A')} | Valor: R$ {recibo.get('valor', 'N/A')} | {recibo.get('descricao', '')}"
        info_label = ctk.CTkLabel(
            item_frame, text=info_text, justify="left", wraplength=350)
        info_label.pack(anchor="w", padx=10, pady=8)

        # Botões de ação
        buttons_frame = ctk.CTkFrame(item_frame, fg_color="#3a3a3a")
        buttons_frame.pack(anchor="e", padx=10, pady=(0, 8))

        edit_btn = ctk.CTkButton(
            buttons_frame,
            text="Editar",
            command=lambda: self.edit_recibo(recibo['id']),
            width=80,
            height=25,
            font=("Arial", 10)
        )
        edit_btn.pack(side="left", padx=3)

        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Deletar",
            command=lambda: self.delete_recibo(recibo['id']),
            width=80,
            height=25,
            fg_color="red",
            font=("Arial", 10)
        )
        delete_btn.pack(side="left", padx=3)

    def create_despesa_item(self, despesa):
        """Cria um item de despesa na lista"""
        item_frame = ctk.CTkFrame(
            self.despesas_frame, fg_color="#3a3a3a", corner_radius=8)
        item_frame.pack(fill="x", padx=5, pady=5)

        # Info da despesa
        info_text = f"Data: {despesa.get('data', 'N/A')} | Valor: R$ {despesa.get('valor', 'N/A')} | {despesa.get('descricao', '')}"
        info_label = ctk.CTkLabel(
            item_frame, text=info_text, justify="left", wraplength=350)
        info_label.pack(anchor="w", padx=10, pady=8)

        # Botões de ação
        buttons_frame = ctk.CTkFrame(item_frame, fg_color="#3a3a3a")
        buttons_frame.pack(anchor="e", padx=10, pady=(0, 8))

        edit_btn = ctk.CTkButton(
            buttons_frame,
            text="Editar",
            command=lambda: self.edit_despesa(despesa['id']),
            width=80,
            height=25,
            font=("Arial", 10)
        )
        edit_btn.pack(side="left", padx=3)

        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Deletar",
            command=lambda: self.delete_despesa(despesa['id']),
            width=80,
            height=25,
            fg_color="red",
            font=("Arial", 10)
        )
        delete_btn.pack(side="left", padx=3)

    def export_recibos_csv(self):
        """Exporta os recibos salvos para CSV"""
        try:
            recibos = self.recibos_storage.load_recibos()

            if not recibos:
                messagebox.showwarning(
                    "Aviso", "Nenhum recibo salvo para exportar!")
                return

            # Preparar dados para export
            self.receita_manager.receitas = []  # Resetar

            # Precisamos garantir que os recibos tenham os dados corretos do profissional ATUAL se eles foram salvos sem.
            # Mas os recibos salvos agora já devem ter.
            # O exportador deve pegar o cpf_prof que está no recibo.
            # O user disse: "O campo inscricao será implementado ... do profissional logado".
            # "Campo cpf_prof com o valor do cpf_prof do profissional logado."

            # Atualizar gerenciador com dados do profissional logado para o "Header" (se houvesse) ou para defaults.
            # O manager usa os dados de cada receita individualmente.

            for recibo in recibos:
                # Override ou garantia?
                # Se for exportação GERAL, talvez devesse filtar pelo profissional logado?
                # "Cada profissional cadastrado terá um banco de dados próprio" -> User falou de pacientes.
                # Recibos estão todos em 'recibos_saude.json' misturados? "Implemente... a coluna cpf_prof que será incrementado do profissional logado".
                # Se o JSON é compartilhado, devemos filtrar pelo cpf_prof logado ao exportar e mostrar na lista?
                # O User não pediu explicitamente filtrar a lista visual, mas parece implícito num sistema multi-usuário.
                # Vou filtrar a exportação pelo cpf do logado E garantir que os dados exportados usem os dados dele.

                # Se recibo não tem cpf_prof, assume o do logado (legado).
                # Se tem e é diferente, não exporta? (Sistema multi-usuário real).
                # Vou filtrar: Apenas recibos deste usuário.

                # Mas antes, verificar se devemos filtrar a LISTA visual também.
                # Para MVP, vou filtrar no export.

                r_cpf_prof = recibo.get('cpf_prof')
                current_cpf = self.current_user.get('cpf_prof')

                # Compatibilidade com legados sem cpf_prof -> assumir user atual se for único ou ...
                # Vou assumir que exportamos TUDO que for compatível ou TUDO se for admin?
                # Melhor filtrar pelo CPF. Se r_cpf_prof for vazio, atribui o current.

                if not r_cpf_prof:
                    recibo['cpf_prof'] = current_cpf

                if recibo['cpf_prof'] == current_cpf:
                    self.receita_manager.add_receita(recibo)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"receita_saude_{datetime.now().strftime('%d%m%Y')}.csv"
            )

            if file_path:
                self.receita_manager.export_csv(file_path)
                messagebox.showinfo(
                    "Sucesso", f"Arquivo gerado com sucesso!\n{file_path}")
                self.receita_manager.receitas = []  # Limpar para próximo export

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar CSV: {str(e)}")

    def export_despesas_csv(self):
        """Exporta as despesas salvas para CSV"""
        try:
            despesas = self.despesas_storage.load_despesas()

            if not despesas:
                messagebox.showwarning(
                    "Aviso", "Nenhuma despesa salva para exportar!")
                return

            # Preparar dados para export
            for despesa in despesas:
                self.despesas_manager.add_despesa(despesa)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"despesas_medicas_{datetime.now().strftime('%d%m%Y')}.csv"
            )

            if file_path:
                self.despesas_manager.export_csv(file_path)
                messagebox.showinfo(
                    "Sucesso", f"Arquivo gerado com sucesso!\n{file_path}")
                self.despesas_manager.despesas = []  # Limpar para próximo export

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar CSV: {str(e)}")

    def clear_form_receita(self):
        """Limpa apenas os campos editáveis da receita"""
        editable_fields = ["data", "valor", "descricao",
                           "cpf_pagador", "cpf_benef"]
        for key in editable_fields:
            if key in self.receita_entries:
                widget = self.receita_entries[key]
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set("")
                elif hasattr(widget, 'delete'):
                    widget.delete(0, "end")

        # Limpar multi_date_picker
        if hasattr(self, 'multi_date_picker'):
            self.multi_date_picker.selected_dates = []
            self.multi_date_picker.delete(0, "end")

        self.editing_recibo_id = None
        self.save_recibo_btn.configure(text="Salvar Recibo")

    def on_closing(self):
        """Finaliza a aplicação seguramente"""
        try:
            self.root.destroy()
            self.root.quit()
        except:
            pass


if __name__ == "__main__":
    from ui.login import LoginWindow

    # Executar Login
    login_app = LoginWindow()
    user = login_app.run()

    if user:
        # Tentar desativar tracking de DPI para evitar erro "invalid command name" no fechamento
        try:
            ctk.deactivate_automatic_dpi_awareness()
        except:
            pass

        # Se login com sucesso, iniciar app principal
        root = ctk.CTk()

        # Obter tamanho da tela e configurar janela com 90% do tamanho
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.85)
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        root.geometry(
            f"{window_width}x{window_height}+{x_position}+{y_position}")

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        app = AplicacaoCarneLeao(root, user)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
