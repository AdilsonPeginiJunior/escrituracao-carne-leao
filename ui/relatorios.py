import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
from pathlib import Path
from models.storage import RecibosStorage, PacientesStorage
from models.report_generator import ReportGenerator, RecibosReportManager, ReportDataExtractor


class GerarRelatoriosWindow(ctk.CTkToplevel):
    """Janela para gerenciar geração de relatórios"""

    def __init__(self, parent, profissional_cpf: str = None):
        super().__init__(parent)

        self.title("Gerar Relatórios")
        self.geometry("1000x750")

        self.profissional_cpf = profissional_cpf
        self.recibos_storage = RecibosStorage()
        self.pacientes_storage = None

        self.report_manager = RecibosReportManager()
        self.report_manager.set_storage(
            self.recibos_storage, self.pacientes_storage)

        self.selected_recibos = {}  # Dict: recibo_id -> {recibo, paciente, checkbox}
        self.recibos_list = []
        self.available_templates = []
        self.selected_template = None

        self.load_available_templates()
        self.setup_ui()
        self.load_recibos()

    def load_available_templates(self):
        """Carrega templates disponíveis em modelosRelatorios/"""
        try:
            templates_dir = "modelosRelatorios"
            if os.path.exists(templates_dir):
                self.available_templates = [
                    f for f in os.listdir(templates_dir)
                    if f.endswith('.docx')
                ]
                self.available_templates.sort()
            else:
                self.available_templates = ["RelatorioTemplateCarimboFem.docx"]
        except Exception as e:
            print(f"Erro ao carregar templates: {e}")
            self.available_templates = ["RelatorioTemplateCarimboFem.docx"]

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

        # Container principal com 3 colunas
        main_container = ctk.CTkFrame(self)
        main_container.grid(row=1, column=0, sticky="nsew",
                            padx=20, pady=(0, 20))
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # ===== PAINEL ESQUERDO - Lista de recibos com checkboxes =====
        left_frame = ctk.CTkFrame(main_container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            left_frame,
            text="Recibos (Múltipla Seleção)",
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
        self.recibos_listbox.bind("<Button-1>", self.on_recibo_clicked)
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
            text="Selecionar Tudo",
            command=self.select_all_recibos,
            fg_color="blue"
        ).grid(row=0, column=1, padx=5, sticky="ew")

        # ===== PAINEL CENTRAL - Seleção de Templates =====
        center_frame = ctk.CTkFrame(main_container)
        center_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            center_frame,
            text="Template Padrão",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, pady=10)

        ctk.CTkLabel(
            center_frame,
            text="Para pacientes com 'Gera Relatório = Sim':",
            font=("Arial", 9, "italic"),
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        # Combo para templates padrão
        self.template_combo = ctk.CTkComboBox(
            center_frame,
            values=self.available_templates,
            command=self.on_template_selected,
            state="readonly"
        )
        self.template_combo.grid(row=2, column=0, sticky="ew", pady=5)

        if self.available_templates:
            self.template_combo.set(self.available_templates[0])
            self.selected_template = self.available_templates[0]

        # Informações sobre templates
        info_divider = ctk.CTkLabel(
            center_frame,
            text="─" * 40,
            text_color="gray"
        )
        info_divider.grid(row=3, column=0, sticky="ew", pady=10)

        # Info sobre configurações do paciente
        info_label = ctk.CTkLabel(
            center_frame,
            text="Templates Configurados",
            font=("Arial", 12, "bold")
        )
        info_label.grid(row=4, column=0, sticky="ew", pady=(5, 10))

        self.patient_info_box = ctk.CTkScrollableFrame(
            center_frame,
            fg_color="gray20"
        )
        self.patient_info_box.grid(row=5, column=0, sticky="nsew")
        self.patient_info_box.grid_columnconfigure(0, weight=1)

        # ===== PAINEL DIREITO - Detalhes e Ações =====
        right_frame = ctk.CTkFrame(main_container)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            right_frame,
            text="Ações e Configurações",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, pady=10)

        # Pasta de saída
        ctk.CTkLabel(
            right_frame,
            text="Pasta de Saída:",
            font=("Arial", 10, "bold")
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        output_button_frame = ctk.CTkFrame(right_frame)
        output_button_frame.grid(row=2, column=0, sticky="ew", pady=5)
        output_button_frame.grid_columnconfigure(0, weight=1)

        self.output_label = ctk.CTkLabel(
            output_button_frame,
            text="Desktop",
            text_color="cyan",
            font=("Arial", 10)
        )
        self.output_label.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            output_button_frame,
            text="Mudar",
            command=self.choose_output_folder,
            width=60
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))

        self.output_folder = os.path.expanduser("~/Desktop")

        # Resumo de seleção
        ctk.CTkLabel(
            right_frame,
            text="Resumo de Seleção",
            font=("Arial", 10, "bold")
        ).grid(row=3, column=0, sticky="w", pady=(20, 5))

        self.summary_box = ctk.CTkScrollableFrame(
            right_frame,
            fg_color="gray20",
            height=150
        )
        self.summary_box.grid(row=4, column=0, sticky="nsew", pady=5)
        self.summary_box.grid_columnconfigure(0, weight=1)

        self.summary_label = ctk.CTkLabel(
            self.summary_box,
            text="Nenhum recibo selecionado",
            text_color="gray",
            justify="left"
        )
        self.summary_label.pack(padx=10, pady=10)

        # Botões de ação
        action_frame = ctk.CTkFrame(right_frame)
        action_frame.grid(row=5, column=0, sticky="ew", pady=20)
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            action_frame,
            text="Gerar Relatórios",
            command=self.generate_selected_reports,
            fg_color="green",
            text_color="white",
            font=("Arial", 12, "bold"),
            height=40
        ).grid(row=0, column=0, columnspan=2, padx=5, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            action_frame,
            text="Desselecionar Tudo",
            command=self.deselect_all_recibos,
            fg_color="gray"
        ).grid(row=1, column=0, padx=5, sticky="ew")

        ctk.CTkButton(
            action_frame,
            text="Fechar",
            command=self.destroy,
            fg_color="darkgray"
        ).grid(row=1, column=1, padx=5, sticky="ew")

    def load_recibos(self):
        """Carrega lista de recibos"""
        try:
            self.recibos_list = self.recibos_storage.load_recibos()
            self.update_recibos_display()
            self.selected_recibos = {}  # Limpar seleção ao recarregar
            self.update_summary()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar recibos: {e}")

    def update_recibos_display(self):
        """Atualiza exibição da lista de recibos com checkboxes"""
        self.recibos_listbox.configure(state="normal")
        self.recibos_listbox.delete("1.0", "end")

        for idx, recibo in enumerate(self.recibos_list, 1):
            recibo_id = recibo.get('id')
            cpf_pagador = recibo.get('cpf_pagador', 'N/A')
            data = recibo.get('data', 'N/A')
            valor = recibo.get('valor', 'N/A')

            # Verificar se paciente gera relatório
            paciente = self._find_paciente(recibo)
            gera_relatorio = "---"
            if paciente:
                gera = paciente.get('gera_relatorio', 'Não')
                if gera == "Sim":
                    gera_relatorio = "✓ Sim"
                elif gera == "Não":
                    gera_relatorio = "✗ Não"
                else:
                    gera_relatorio = f"✓ {gera[:20]}"  # Template específico

            # Checkbox marcado?
            checkbox = "[✓]" if recibo_id in self.selected_recibos else "[ ]"

            texto = f"{checkbox} {idx}. {data} | CPF: {cpf_pagador} | R$ {valor} | Relatório: {gera_relatorio}\n"
            self.recibos_listbox.insert("end", texto)

        self.recibos_listbox.configure(state="disabled")

    def on_recibo_clicked(self, event=None):
        """Evento ao clicar na listbox - toggle checkbox"""
        # Obter linha clicada
        try:
            line_index = self.recibos_listbox.index(f"@{event.x},{event.y}")
            line_num = int(line_index.split(".")[0])

            if 0 < line_num <= len(self.recibos_list):
                recibo_id = self.recibos_list[line_num - 1].get('id')
                if recibo_id in self.selected_recibos:
                    del self.selected_recibos[recibo_id]
                else:
                    self.selected_recibos[recibo_id] = self.recibos_list[line_num - 1]

                self.update_recibos_display()
                self.update_summary()
        except:
            pass

    def select_all_recibos(self):
        """Seleciona todos os recibos que têm gera_relatorio != Não"""
        for recibo in self.recibos_list:
            recibo_id = recibo.get('id')
            paciente = self._find_paciente(recibo)
            if paciente:
                gera = paciente.get('gera_relatorio', 'Não')
                if gera != "Não":
                    self.selected_recibos[recibo_id] = recibo
            else:
                # Se não achar paciente, incluir mesmo assim
                self.selected_recibos[recibo_id] = recibo

        self.update_recibos_display()
        self.update_summary()
        messagebox.showinfo(
            "Info", f"{len(self.selected_recibos)} recibos selecionados")

    def deselect_all_recibos(self):
        """Desseleciona todos os recibos"""
        self.selected_recibos = {}
        self.update_recibos_display()
        self.update_summary()

    def on_template_selected(self, choice):
        """Evento ao selecionar um template"""
        self.selected_template = choice

    def update_summary(self):
        """Atualiza resumo de seleção"""
        if not self.selected_recibos:
            self.summary_label.configure(text="Nenhum recibo selecionado")
            return

        summary_text = f"Total: {len(self.selected_recibos)} recibo(s)\n\n"

        for recibo_id, recibo in self.selected_recibos.items():
            paciente = self._find_paciente(recibo)
            cpf = recibo.get('cpf_pagador', 'N/A')
            data = recibo.get('data', 'N/A')

            if paciente:
                nome = paciente.get(
                    'nome_benef', paciente.get('nome_pagador', 'N/A'))
                gera = paciente.get('gera_relatorio', 'Não')

                if gera == "Não":
                    status = "❌ Não gera"
                elif gera == "Sim":
                    status = "✓ Padrão"
                else:
                    status = f"✓ {gera[:15]}"

                summary_text += f"• {data} - {nome[:20]} ({cpf}) - {status}\n"
            else:
                summary_text += f"• {data} - CPF {cpf} - ? Paciente não encontrado\n"

        self.summary_label.configure(text=summary_text)

    def update_patient_info(self):
        """Atualiza informações de relatórios dos pacientes selecionados"""
        # Limpar box anterior
        for widget in self.patient_info_box.winfo_children():
            widget.destroy()

        if not self.selected_recibos:
            ctk.CTkLabel(
                self.patient_info_box,
                text="Selecione recibos para ver info",
                text_color="gray"
            ).pack(padx=10, pady=10)
            return

        for recibo_id, recibo in self.selected_recibos.items():
            paciente = self._find_paciente(recibo)
            if not paciente:
                continue

            gera = paciente.get('gera_relatorio', 'Não')

            frame = ctk.CTkFrame(self.patient_info_box, fg_color="gray25")
            frame.pack(fill="x", padx=5, pady=5)

            nome = paciente.get(
                'nome_benef', paciente.get('nome_pagador', 'N/A'))
            ctk.CTkLabel(
                frame,
                text=f"{nome[:25]}",
                font=("Arial", 10, "bold"),
                text_color="cyan"
            ).pack(anchor="w", padx=5, pady=(5, 2))

            if gera == "Não":
                ctk.CTkLabel(
                    frame,
                    text="❌ NÃO gera relatório",
                    text_color="red",
                    font=("Arial", 9)
                ).pack(anchor="w", padx=10, pady=(0, 5))
            elif gera == "Sim":
                ctk.CTkLabel(
                    frame,
                    text="✓ Usa template padrão",
                    text_color="green",
                    font=("Arial", 9)
                ).pack(anchor="w", padx=10, pady=(0, 5))
            else:
                ctk.CTkLabel(
                    frame,
                    text=f"✓ Template: {gera}",
                    text_color="yellow",
                    font=("Arial", 9)
                ).pack(anchor="w", padx=10, pady=(0, 5))

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

    def validate_and_generate_report(self, recibo, paciente):
        """Valida se pode gerar relatório e o gera"""
        gera = paciente.get('gera_relatorio', 'Não')

        # Se não gera, retornar erro
        if gera == "Não":
            return False, "Paciente não está configurado para gerar relatórios"

        # Determinar qual template usar
        if gera == "Sim":
            # Usar o selecionado na UI
            template = self.selected_template
        else:
            # Usar o template específico do paciente
            template = gera

        # Validar se template existe
        template_path = os.path.join("modelosRelatorios", template)
        if not os.path.exists(template_path):
            return False, f"Template não encontrado: {template}"

        # Gerar nome do arquivo
        variables = ReportDataExtractor.extract_report_variables(
            recibo, paciente)
        nome_beneficiario = variables['#NomePac']
        ano = variables['#AnoDasConsultas2']
        mes = variables['#MesDasConsultas2']

        # Limpar nome para usar como filename
        import re
        nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome_beneficiario).strip()

        # Criar pasta específica do mês se não existir
        mes_capitalizado = mes.capitalize() if mes else "Sem_Mês"
        pasta_mes = f"Relatório de {mes_capitalizado}"
        caminho_mes = os.path.join(self.output_folder, pasta_mes)

        if not os.path.exists(caminho_mes):
            try:
                os.makedirs(caminho_mes, exist_ok=True)
            except Exception as e:
                print(f"Erro ao criar pasta {caminho_mes}: {e}")
                return False, f"Erro ao criar pasta de relatórios: {e}"

        output_filename = f"{nome_limpo} - Relatório {ano}{mes.capitalize()}.pdf"
        output_path = os.path.join(caminho_mes, output_filename)

        # Gerar relatório
        report_gen = ReportGenerator(template_path)
        success = report_gen.generate_report(recibo, paciente, output_path)

        if success:
            return True, f"Relatório gerado: {output_filename}"
        else:
            return False, f"Erro ao gerar relatório para {nome_beneficiario}"

    def generate_selected_reports(self):
        """Gera relatórios para todos os recibos selecionados"""
        if not self.selected_recibos:
            messagebox.showwarning("Aviso", "Selecione pelo menos um recibo")
            return

        successful = 0
        failed = 0
        errors = []

        # Atualizar info de pacientes
        self.update_patient_info()

        for recibo_id, recibo in self.selected_recibos.items():
            paciente = self._find_paciente(recibo)

            if not paciente:
                failed += 1
                errors.append(
                    f"Paciente não encontrado para CPF {recibo.get('cpf_pagador')}")
                continue

            success, message = self.validate_and_generate_report(
                recibo, paciente)

            if success:
                successful += 1
                print(f"✓ {message}")
            else:
                failed += 1
                errors.append(f"❌ {message}")
                print(f"✗ {message}")

        # Mostrar resultado
        result_msg = f"Gerados com sucesso: {successful}\nErros: {failed}"
        if errors:
            result_msg += "\n\nDetalhes dos erros:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_msg += f"\n... e mais {len(errors) - 5} erro(s)"

        messagebox.showinfo("Resultado", result_msg)

    def choose_output_folder(self):
        """Permite escolher pasta de saída"""
        folder = filedialog.askdirectory(
            title="Escolher pasta para salvar relatórios",
            initialdir=self.output_folder
        )
        if folder:
            self.output_folder = folder
            folder_display = folder.replace(os.path.expanduser("~"), "~")
            self.output_label.configure(text=folder_display)
