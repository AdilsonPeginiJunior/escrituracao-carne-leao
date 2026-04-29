import customtkinter as ctk
import json
import os
from tkinter import messagebox

class CategoriaDespesaWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Gerenciar Categorias de Despesas")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Centralizar
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        self.file_path = "categorias_despesas.json"
        
        self.setup_ui()
        self.load_categorias()
        
        self.editing_code = None
        
    def setup_ui(self):
        # Frame de formulário
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="Código (Ex: P10.01.00001):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.code_entry = ctk.CTkEntry(form_frame, width=150)
        self.code_entry.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Descrição:").grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.desc_entry = ctk.CTkEntry(form_frame, width=380)
        self.desc_entry.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 10))
        
        # Botões do formulário
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="e", padx=5, pady=5)
        
        self.save_btn = ctk.CTkButton(btn_frame, text="Adicionar", command=self.save_categoria, width=100)
        self.save_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Limpar", command=self.clear_form, width=100, fg_color="gray").pack(side="left", padx=5)
        
        # Lista com pesquisa
        list_container = ctk.CTkFrame(self)
        list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        search_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(search_frame, text="Pesquisar:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=300)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_list)
        
        # Scrollable Frame para os itens
        self.scroll_frame = ctk.CTkScrollableFrame(list_container)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
    def load_categorias(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.categorias = json.load(f)
            else:
                self.categorias = []
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar categorias: {e}")
            self.categorias = []
            
        self.refresh_list()
        
    def refresh_list(self, filter_text=""):
        # Limpar lista
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        filter_text = filter_text.lower()
        
        sorted_categorias = sorted(self.categorias, key=lambda x: x['codigo'])
        
        for cat in sorted_categorias:
            if filter_text and (filter_text not in cat['codigo'].lower() and filter_text not in cat['descricao'].lower()):
                continue
                
            item_frame = ctk.CTkFrame(self.scroll_frame)
            item_frame.pack(fill="x", pady=2, padx=2)
            
            ctk.CTkLabel(item_frame, text=f"{cat['codigo']} - {cat['descricao']}", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(item_frame, text="Editar", width=60, height=24, command=lambda c=cat: self.edit_categoria(c)).pack(side="right", padx=2, pady=2)
            ctk.CTkButton(item_frame, text="Excluir", width=60, height=24, fg_color="red", command=lambda c=cat: self.delete_categoria(c)).pack(side="right", padx=2, pady=2)
            
    def filter_list(self, event=None):
        self.refresh_list(self.search_entry.get())
        
    def save_categoria(self):
        codigo = self.code_entry.get().strip()
        descricao = self.desc_entry.get().strip()
        
        if not codigo or not descricao:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
            
        # Validar duplicidade
        if not self.editing_code:
            for cat in self.categorias:
                if cat['codigo'] == codigo:
                    messagebox.showerror("Erro", "Código já existe!")
                    return
        
        if self.editing_code:
            # Atualizar
            for i, cat in enumerate(self.categorias):
                if cat['codigo'] == self.editing_code:
                    uso_atual = cat.get('contagem_uso', 0)
                    self.categorias[i] = {
                        "codigo": codigo, 
                        "descricao": descricao,
                        "contagem_uso": uso_atual
                    }
                    break
        else:
            # Novo
            self.categorias.append({
                "codigo": codigo, 
                "descricao": descricao,
                "contagem_uso": 0
            })
            
        self.save_to_file()
        self.clear_form()
        self.refresh_list()
        
    def save_to_file(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.categorias, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {e}")
            
    def edit_categoria(self, cat):
        self.code_entry.delete(0, "end")
        self.code_entry.insert(0, cat['codigo'])
        self.desc_entry.delete(0, "end")
        self.desc_entry.insert(0, cat['descricao'])
        
        self.editing_code = cat['codigo']
        self.save_btn.configure(text="Atualizar")
        
    def delete_categoria(self, cat):
        if messagebox.askyesno("Confirmar", f"Excluir categoria {cat['codigo']}?"):
            self.categorias = [c for c in self.categorias if c['codigo'] != cat['codigo']]
            self.save_to_file()
            self.refresh_list()
            
    def clear_form(self):
        self.code_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.editing_code = None
        self.save_btn.configure(text="Adicionar")
