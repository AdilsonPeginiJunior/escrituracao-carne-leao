import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from models.auth import AuthManager

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Acesso ao Sistema - Carnê Leão")
        self.geometry("400x450")
        self.resizable(False, False)
        
        # Centralizar na tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 450) // 2
        self.geometry(f"400x450+{x}+{y}")
        
        self.auth_manager = AuthManager()
        self.logged_user = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Título
        title_label = ctk.CTkLabel(
            self, 
            text="Bem-vindo(a)", 
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(40, 20))
        
        subtitle_label = ctk.CTkLabel(
            self, 
            text="Selecione seu usuário para entrar", 
            font=("Arial", 14),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Frame de credenciais
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="x", padx=40)
        
        # Seleção de usuário
        ctk.CTkLabel(form_frame, text="Profissional", anchor="w").pack(fill="x", pady=(0, 5))
        
        usuarios = self.auth_manager.get_all_users()
        self.user_combo = ctk.CTkComboBox(
            form_frame,
            values=usuarios,
            height=35,
            width=320
        )
        self.user_combo.pack(fill="x", pady=(0, 15))
        
        if usuarios:
            self.user_combo.set(usuarios[0])
        else:
            self.user_combo.set("")
            
        # Senha
        ctk.CTkLabel(form_frame, text="Senha", anchor="w").pack(fill="x", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            show="*",
            height=35,
            width=320,
            placeholder_text="Digite sua senha"
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Botão Entrar
        self.login_button = ctk.CTkButton(
            self,
            text="ENTRAR NO SISTEMA",
            command=self.login,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.login_button.pack(padx=40, pady=10, fill="x")
        
        # Bind enter key
        self.bind('<Return>', lambda event: self.login())
        
    def login(self):
        usuario = self.user_combo.get()
        senha = self.password_entry.get()
        
        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
            
        user_data = self.auth_manager.login(usuario, senha)
        
        if user_data:
            self.logged_user = user_data
            self.destroy() # Fecha janela de login e encerra mainloop do login
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    def run(self):
        self.mainloop()
        return self.logged_user
