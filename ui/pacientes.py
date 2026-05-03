import customtkinter as ctk
from tkinter import messagebox
from models.storage import PacientesStorage
# Helper para format_cpf ? Melhor duplicar ou importar static
from app import AplicacaoCarneLeao
# Para evitar circular imports, duplicarei os helpers estáticos ou moverei para um utils comum.
# Helper de formatação simples aqui por enquanto


def format_cpf_display(v):
    v = "".join(filter(str.isdigit, str(v)))
    if len(v) != 11:
        return v
    return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"


def clean_cpf_save(v):
    return "".join(filter(str.isdigit, str(v)))


class CadastroPacientesWindow(ctk.CTkToplevel):
    def __init__(self, parent, pacientes_file):
        super().__init__(parent)

        self.title("Cadastro de Pacientes")
        self.geometry("700x600")

        # O arquivo de pacientes depende do profissional logado, passado pelo parent ou controller
        self.storage = PacientesStorage(pacientes_file)
        self.editing_id = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Gerenciar Pacientes", font=(
            "Arial", 20, "bold")).grid(row=0, column=0, pady=20)

        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        container.grid_columnconfigure(0, weight=1)  # Form
        container.grid_columnconfigure(1, weight=1)  # List
        container.grid_rowconfigure(0, weight=1)

        # Form
        form_frame = ctk.CTkScrollableFrame(
            container, label_text="Dados do Paciente")
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.entries = {}
        fields = [
            ("Nome Pagador", "nome_pagador"),
            ("CPF Pagador", "cpf_pagador"),
            ("Nome Beneficiário", "nome_benef"),
            ("CPF Beneficiário", "cpf_benef"),
            ("Valor Consulta (R$)", "valor_cons"),
            ("Código CID", "cod_cid"),
            ("Início Tratamento", "inicio")
        ]

        for lbl, key in fields:
            ctk.CTkLabel(form_frame, text=lbl).pack(anchor="w", padx=5)
            entry = ctk.CTkEntry(form_frame)
            entry.pack(fill="x", padx=5, pady=(0, 10))
            self.entries[key] = entry

        # Campos adicionais solicitados (mesma linha)
        row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=5, pady=(0, 10))

        gen_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        gen_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(gen_frame, text="Genero").pack(anchor="w")
        genero_cb = ctk.CTkComboBox(gen_frame, values=["Fem", "Masc"])
        genero_cb.pack(fill="x")
        genero_cb.set("")
        self.entries['genero'] = genero_cb

        gera_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        gera_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(gera_frame, text="Gera Relatório").pack(anchor="w")
        gera_cb = ctk.CTkComboBox(gera_frame, values=["Sim", "Não", "_RelatorioTemplateCamila.docx","_RelatorioTemplateCarimboFem.docx", "_RelatorioTemplateCarimboFemCid32.docx", "_RelatorioTemplateCarimboMasc.docx", "_RelatorioTemplateDanilo.docx", "_RelatorioTemplateDigitalFem.docx", "_RelatorioTemplateDigitalMasc.docx"])
        gera_cb.pack(fill="x")
        gera_cb.set("")
        self.entries['gera_relatorio'] = gera_cb

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)

        self.btn_save = ctk.CTkButton(
            btn_frame, text="Salvar Paciente", command=self.save, fg_color="green")
        self.btn_save.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(btn_frame, text="Novo Cadastro", command=self.clear_form,
                      fg_color="gray").pack(side="left", padx=5, expand=True, fill="x")

        # List
        list_frame = ctk.CTkFrame(container)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(list_frame, text="Pacientes Cadastrados").pack(pady=5)
        self.list_scroll = ctk.CTkScrollableFrame(list_frame)
        self.list_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def load_data(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()

        pacientes = self.storage.load_pacientes()

        for p in pacientes:
            item = ctk.CTkFrame(self.list_scroll)
            item.pack(fill="x", pady=2)

            cpf_pag_fmt = format_cpf_display(p.get('cpf_pagador', ''))
            lbl_text = f"{p.get('nome_pagador')} ({cpf_pag_fmt})"

            ctk.CTkLabel(item, text=lbl_text, anchor="w").pack(
                side="left", padx=5, fill="x", expand=True)

            ctk.CTkButton(item, text="X", width=30, fg_color="red",
                          command=lambda x=p['id']: self.delete(x)).pack(side="right", padx=2)
            ctk.CTkButton(item, text="E", width=30, command=lambda x=p: self.edit(x)).pack(
                side="right", padx=2)

    def save(self):
        data = {k: v.get() for k, v in self.entries.items()}

        # Validation
        if not data['nome_pagador']:
            messagebox.showerror("Erro", "Nome do Pagador é obrigatório.")
            return

        # Clean CPFs
        if data.get('cpf_pagador'):
            data['cpf_pagador'] = clean_cpf_save(data['cpf_pagador'])
        if data.get('cpf_benef'):
            data['cpf_benef'] = clean_cpf_save(data['cpf_benef'])

        # Normalizar opções de combo (garantir valores esperados)
        if 'genero' in data and data['genero'] not in ('Fem', 'Masc'):
            data['genero'] = ''
        if 'gera_relatorio' in data and data['gera_relatorio'] not in ('Sim', 'Não'):
            data['gera_relatorio'] = ''

        try:
            if self.editing_id:
                self.storage.update_paciente(self.editing_id, data)
                messagebox.showinfo("Sucesso", "Paciente atualizado!")
            else:
                self.storage.save_paciente(data)
                messagebox.showinfo("Sucesso", "Paciente cadastrado!")

            self.clear_form()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def edit(self, data):
        self.editing_id = data['id']
        self.btn_save.configure(text="Atualizar Paciente")

        for k, v in self.entries.items():
            val = data.get(k, '')
            # Format CPFs for display
            if k in ['cpf_pagador', 'cpf_benef']:
                val = format_cpf_display(val)

            # Limpar o widget de forma compatível (Entry ou ComboBox)
            if hasattr(v, 'delete'):
                try:
                    v.delete(0, 'end')
                except Exception:
                    pass
            else:
                try:
                    v.set('')
                except Exception:
                    pass

            # Preencher o valor: ComboBox usa set(), Entry usa insert()
            try:
                v.set(str(val))
            except Exception:
                try:
                    v.insert(0, str(val))
                except Exception:
                    pass

    def delete(self, pid):
        if messagebox.askyesno("Confirmar", "Deletar paciente?"):
            self.storage.delete_paciente(pid)
            self.load_data()

    def clear_form(self):
        self.editing_id = None
        self.btn_save.configure(text="Salvar Paciente")
        for v in self.entries.values():
            if hasattr(v, 'delete'):
                try:
                    v.delete(0, 'end')
                except Exception:
                    pass
            else:
                try:
                    v.set('')
                except Exception:
                    pass
