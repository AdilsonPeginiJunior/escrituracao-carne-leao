import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
from models.storage import RecibosStorage, PacientesStorage
from models.report_generator import ReportGenerator, RecibosReportManager, ReportDataExtractor


class GerarRelatoriosWindow(ctk.CTkToplevel):
    """Janela para gerenciar geração de relatórios"""

    def __init__(self, parent, profissional_cpf: str = None):
        super().__init__(parent)

        self.title("Gerar Relatórios")
        self.geometry("900x700")

        self.profissional_cpf = profissional_cpf
        self.recibos_storage = RecibosStorage()
        self.pacientes_storage = None

        self.report_manager = RecibosReportManager()
        self.report_manager.set_storage(
            self.recibos_storage, self.pacientes_storage)

        self.selected_recibo_id = None
        self.recibos_list = []

        self.setup_ui()
        self.load_recibos()

    def setup_ui(self):
        """Configura a interface"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Cabeçalho
        header = ctk.CTkLabel(
            self,
            text="Gerar Relatórios de Recibos",
            font=("Arial", 20, "bold")
        )
        header.grid(row=0, column=0, pady=20, padx=20)

        # Container principal
        main_container = ctk.CTkFrame(self)
        main_container.grid(row=1, column=0, sticky="nsew",
                            padx=20, pady=(0, 20))
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Painel esquerdo - Lista de recibos
        left_frame = ctk.CTkFrame(main_container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            left_frame,
            text="Recibos Disponíveis",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, pady=10)

        # Frame com scrollbar para lista
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        scrollbar = ctk.CTkScrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.recibos_listbox = ctk.CTkTextbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=300,
            width=300,
            state="disabled"
        )
        self.recibos_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.configure(command=self.recibos_listbox.yview)

        # Botões para lista
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            button_frame,
            text="Atualizar",
            command=self.load_recibos
        ).grid(row=0, column=0, padx=5, sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Selecionar",
            command=self.select_recibo_from_list,
            fg_color="green"
        ).grid(row=0, column=1, padx=5, sticky="ew")

        # Painel direito - Informações e ações
        right_frame = ctk.CTkFrame(main_container)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            right_frame,
            text="Detalhes do Recibo",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, pady=10)

        # Info box
        info_frame = ctk.CTkFrame(right_frame)
        info_frame.grid(row=1, column=0, sticky="ew", pady=10)
        info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(info_frame, text="CPF Pagador:").grid(
            row=0, column=0, sticky="w", pady=5)
        self.info_cpf_pagador = ctk.CTkLabel(
            info_frame, text="---", text_color="gray")
        self.info_cpf_pagador.grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkLabel(info_frame, text="CPF Beneficiário:").grid(
            row=1, column=0, sticky="w", pady=5)
        self.info_cpf_benef = ctk.CTkLabel(
            info_frame, text="---", text_color="gray")
        self.info_cpf_benef.grid(row=1, column=1, sticky="w", padx=10)

        ctk.CTkLabel(info_frame, text="Paciente:").grid(
            row=2, column=0, sticky="w", pady=5)
        self.info_paciente = ctk.CTkLabel(
            info_frame, text="---", text_color="gray")
        self.info_paciente.grid(row=2, column=1, sticky="w", padx=10)

        ctk.CTkLabel(info_frame, text="Descrição:").grid(
            row=3, column=0, sticky="w", pady=5)
        self.info_descricao = ctk.CTkLabel(
            info_frame,
            text="---",
            text_color="gray",
            wraplength=200,
            justify="left"
        )
        self.info_descricao.grid(row=3, column=1, sticky="ew", padx=10)

        # Preview de variáveis
        preview_frame = ctk.CTkScrollableFrame(
            right_frame,
            label_text="Variáveis do Relatório"
        )
        preview_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        preview_frame.grid_columnconfigure(0, weight=1)

        self.preview_labels = {}
        variables_preview = [
            "#NomePac",
            "#CPF",
            "#DtInicioAtend",
            "#NrSessoes",
            "#DataDasCons",
            "#UltDiaMesConsultas",
            "#MesDasConsultas2",
            "#AnoDasConsultas2",
            "#FormaPresencial"
        ]

        for idx, var in enumerate(variables_preview):
            label_frame = ctk.CTkFrame(preview_frame)
            label_frame.grid(row=idx, column=0, sticky="ew", pady=3)
            label_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(label_frame, text=f"{var}:").grid(
                row=0, column=0, sticky="w")
            value_label = ctk.CTkLabel(
                label_frame, text="---", text_color="gray")
            value_label.grid(row=0, column=1, sticky="ew", padx=10)
            self.preview_labels[var] = value_label

        # Botões de ação
        action_frame = ctk.CTkFrame(right_frame)
        action_frame.grid(row=3, column=0, sticky="ew", pady=20)
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            action_frame,
            text="Gerar Relatório",
            command=self.generate_report,
            fg_color="green",
            text_color="white",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=5, sticky="ew")

        ctk.CTkButton(
            action_frame,
            text="Escolher Pasta",
            command=self.choose_output_folder,
            text_color="white"
        ).grid(row=0, column=1, padx=5, sticky="ew")

        self.output_label = ctk.CTkLabel(
            right_frame,
            text="Pasta de saída: Desktop",
            text_color="gray",
            font=("Arial", 10)
        )
        self.output_label.grid(row=4, column=0, sticky="ew", pady=5)

        self.output_folder = os.path.expanduser("~/Desktop")

    def load_recibos(self):
        """Carrega lista de recibos"""
        try:
            self.recibos_list = self.recibos_storage.load_recibos()
            self.update_recibos_display()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar recibos: {e}")

    def update_recibos_display(self):
        """Atualiza exibição da lista de recibos"""
        self.recibos_listbox.configure(state="normal")
        self.recibos_listbox.delete("1.0", "end")

        for idx, recibo in enumerate(self.recibos_list, 1):
            cpf_pagador = recibo.get('cpf_pagador', 'N/A')
            data = recibo.get('data', 'N/A')
            valor = recibo.get('valor', 'N/A')

            texto = f"{idx}. Data: {data} | CPF: {cpf_pagador} | Valor: R$ {valor}\n"
            self.recibos_listbox.insert("end", texto)

        self.recibos_listbox.configure(state="disabled")

    def select_recibo_from_list(self):
        """Abre dialog para selecionar recibo da lista"""
        if not self.recibos_list:
            messagebox.showwarning("Aviso", "Nenhum recibo disponível")
            return

        # Criar lista de opções
        opcoes = []
        for idx, recibo in enumerate(self.recibos_list):
            cpf = recibo.get('cpf_pagador', 'N/A')
            data = recibo.get('data', 'N/A')
            opcoes.append(f"{idx}: {data} - CPF {cpf}")

        # Criar janela de seleção simplificada
        self.show_selection_dialog(opcoes)

    def show_selection_dialog(self, opcoes):
        """Mostra diálogo para seleção"""
        # Simplificado: usar primeira opção da UI como selecionada
        # Em uma solução completa, teríamos um diálogo de lista
        if opcoes:
            # Usar o primeiro recibo como padrão
            self.selected_recibo_id = self.recibos_list[0].get('id')
            self.update_recibo_details()

    def update_recibo_details(self):
        """Atualiza detalhes do recibo selecionado"""
        if not self.selected_recibo_id:
            return

        recibo = None
        for r in self.recibos_list:
            if r.get('id') == self.selected_recibo_id:
                recibo = r
                break

        if not recibo:
            messagebox.showerror("Erro", "Recibo não encontrado")
            return

        # Atualizar informações básicas
        self.info_cpf_pagador.configure(text=recibo.get('cpf_pagador', 'N/A'))
        self.info_cpf_benef.configure(text=recibo.get('cpf_benef', 'N/A'))
        self.info_descricao.configure(text=recibo.get('descricao', 'N/A'))

        # Buscar paciente
        paciente = self._find_paciente(recibo)
        if paciente:
            self.info_paciente.configure(
                text=f"{paciente.get('nome_pagador', 'N/A')} / {paciente.get('nome_benef', 'N/A')}"
            )
        else:
            self.info_paciente.configure(text="Não encontrado")

        # Atualizar preview de variáveis
        if paciente:
            variables = ReportDataExtractor.extract_report_variables(
                recibo, paciente)
            for var_name, var_value in variables.items():
                if var_name in self.preview_labels:
                    self.preview_labels[var_name].configure(
                        text=str(var_value)[:50])

    def _find_paciente(self, recibo):
        """Procura paciente do recibo"""
        try:
            cpf_benef = recibo.get('cpf_benef', '').strip()
            cpf_pagador = recibo.get('cpf_pagador', '').strip()
            cpf_procurado = cpf_benef if cpf_benef and cpf_benef != cpf_pagador else cpf_pagador

            # Procurar em arquivos de profissionais
            for file in os.listdir("."):
                if file.endswith("_pacientes.json"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            pacientes = data.get('pacientes', [])

                            for paciente in pacientes:
                                cpf_b = paciente.get('cpf_benef', '').strip()
                                cpf_p = paciente.get('cpf_pagador', '').strip()

                                if cpf_b == cpf_procurado or cpf_p == cpf_procurado:
                                    return paciente
                    except Exception as e:
                        continue

            return None
        except Exception as e:
            print(f"Erro ao procurar paciente: {e}")
            return None

    def generate_report(self):
        """Gera relatório para recibo selecionado"""
        if not self.selected_recibo_id:
            messagebox.showwarning("Aviso", "Selecione um recibo primeiro")
            return

        try:
            # Buscar recibo e paciente
            recibo = None
            for r in self.recibos_list:
                if r.get('id') == self.selected_recibo_id:
                    recibo = r
                    break

            if not recibo:
                messagebox.showerror("Erro", "Recibo não encontrado")
                return

            paciente = self._find_paciente(recibo)
            if not paciente:
                messagebox.showerror("Erro", "Paciente não encontrado")
                return

            # Gerar nome do arquivo
            variables = ReportDataExtractor.extract_report_variables(
                recibo, paciente)
            nome_beneficiario = variables['#NomePac']
            ano = variables['#AnoDasConsultas2']
            mes = variables['#MesDasConsultas2']

            # Limpar nome para usar como filename
            import re
            nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome_beneficiario).strip()

            output_filename = f"{nome_limpo} - Relatório {ano}{mes.capitalize()}.pdf"
            output_path = os.path.join(self.output_folder, output_filename)

            # Gerar relatório
            report_gen = ReportGenerator()
            success = report_gen.generate_report(recibo, paciente, output_path)

            if success:
                messagebox.showinfo(
                    "Sucesso",
                    f"Relatório gerado com sucesso:\n{output_filename}"
                )
            else:
                messagebox.showerror("Erro", "Erro ao gerar relatório")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
            print(f"Erro detalhado: {e}")

    def choose_output_folder(self):
        """Permite escolher pasta de saída"""
        folder = filedialog.askdirectory(
            title="Escolher pasta para salvar relatórios",
            initialdir=self.output_folder
        )
        if folder:
            self.output_folder = folder
            folder_display = folder.replace(os.path.expanduser("~"), "~")
            self.output_label.configure(
                text=f"Pasta de saída: {folder_display}")
