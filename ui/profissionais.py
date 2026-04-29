import customtkinter as ctk
from tkinter import messagebox
from models.storage import ProfissionaisStorage

class CadastroProfissionaisWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.on_close_callback = on_close_callback
        
        self.title("Cadastro de Profissionais")
        self.geometry("600x500")
        
        self.storage = ProfissionaisStorage()
        self.editing_id = None
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Título
        ctk.CTkLabel(self, text="Gerenciar Profissionais", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=20)
        
        # Container
        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # Form
        form_frame = ctk.CTkFrame(container)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="Novo/Editar Profissional", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.entries = {}
        fields = [
            ("Apelido (Nome Exibição)", "apelido"),
            ("Usuário (Login)", "usuario"),
            ("Senha", "senha"),
            ("Nº Inscrição", "inscricao"),
            ("CPF Profissional", "cpf_prof")
        ]
        
        for lbl, key in fields:
            ctk.CTkLabel(form_frame, text=lbl).pack(anchor="w", padx=10)
            entry = ctk.CTkEntry(form_frame)
            entry.pack(fill="x", padx=10, pady=(0, 10))
            if key == "senha":
                entry.configure(show="*")
            self.entries[key] = entry
            
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        self.btn_save = ctk.CTkButton(btn_frame, text="Salvar", command=self.save, fg_color="green")
        self.btn_save.pack(side="left", padx=10, expand=True)
        
        ctk.CTkButton(btn_frame, text="Novo Cadastro", command=self.clear_form, fg_color="gray").pack(side="left", padx=10, expand=True)
        
        # List
        list_frame = ctk.CTkFrame(container)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(list_frame, text="Profissionais Cadastrados", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.list_scroll = ctk.CTkScrollableFrame(list_frame)
        self.list_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
    def load_data(self):
        # Limpar lista
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
            
        profs = self.storage.load_profissionais()
        
        for p in profs:
            item = ctk.CTkFrame(self.list_scroll)
            item.pack(fill="x", pady=2)
            
            lbl = ctk.CTkLabel(item, text=f"{p.get('apelido')} ({p.get('usuario')})")
            lbl.pack(side="left", padx=10)
            
            btn_del = ctk.CTkButton(item, text="X", width=30, fg_color="red", command=lambda x=p['id']: self.delete(x))
            btn_del.pack(side="right", padx=2)
            
            btn_edit = ctk.CTkButton(item, text="E", width=30, command=lambda x=p: self.edit(x))
            btn_edit.pack(side="right", padx=2)

    def save(self):
        data = {k: v.get() for k, v in self.entries.items()}
        
        # Simple Validation
        if not data['usuario'] or not data['senha'] or not data['apelido']:
            messagebox.showerror("Erro", "Campos Apelido, Usuário e Senha são obrigatórios.")
            return

        try:
            if self.editing_id:
                self.storage.update_profissional(self.editing_id, data)
                messagebox.showinfo("Sucesso", "Profissional atualizado!")
            else:
                self.storage.save_profissional(data)
                messagebox.showinfo("Sucesso", "Profissional cadastrado!")
            
            self.clear_form()
            self.load_data()
            if self.on_close_callback: self.on_close_callback()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def edit(self, data):
        self.editing_id = data['id']
        self.btn_save.configure(text="Atualizar")
        
        for k, v in self.entries.items():
            if k in data:
                v.delete(0, 'end')
                v.insert(0, data[k])
                
    def delete(self, pid):
        if messagebox.askyesno("Confirmar", "Deletar profissional?"):
            self.storage.delete_profissional(pid)
            self.load_data()
            if self.on_close_callback: self.on_close_callback()

    def clear_form(self):
        self.editing_id = None
        self.btn_save.configure(text="Salvar")
        for v in self.entries.values():
            v.delete(0, 'end')
