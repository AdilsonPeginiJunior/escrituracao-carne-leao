"""Janela para assinatura digital e validação de PDFs (certificados ICP-Brasil A1/A3)."""
import os
import customtkinter as ctk
from tkinter import messagebox, filedialog

from models.assinatura_digital import (
    AssinadorPDF,
    ConfiguracaoAssinaturaVisivel,
    CertificadoInvalidoError,
    SenhaIncorretaError,
    TokenNaoDetectadoError,
    salvar_ultimo_pfx,
    carregar_ultimo_pfx,
)


class AssinaturaDigitalWindow(ctk.CTkToplevel):
    """Janela para assinar digitalmente um PDF com certificado A1 ou A3, e validar assinaturas."""

    def __init__(self, parent, pdf_inicial: str | None = None, pasta_inicial: str | None = None,
                 current_user: dict | None = None):
        super().__init__(parent)

        self.title("Assinatura Digital de PDF (ICP-Brasil)")
        self.geometry("620x760")

        self.pasta_inicial = pasta_inicial or os.path.expanduser("~/Desktop")
        self.assinador = AssinadorPDF()
        self.tipo_certificado = ctk.StringVar(value="A1")
        self.current_user = current_user or {}

        self._setup_ui()

        ultimo_pfx = carregar_ultimo_pfx()
        if ultimo_pfx and os.path.exists(ultimo_pfx):
            self.entry_pfx.insert(0, ultimo_pfx)

        if pdf_inicial:
            self.entry_pdf_entrada.insert(0, pdf_inicial)
            self._sugerir_saida(pdf_inicial)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_ui(self):
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container, text="Assinatura Digital de PDF",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(0, 10))

        # ----- PDF de entrada/saída -----
        pdf_frame = ctk.CTkFrame(container)
        pdf_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(pdf_frame, text="PDF a assinar:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        row1 = ctk.CTkFrame(pdf_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)
        self.entry_pdf_entrada = ctk.CTkEntry(row1)
        self.entry_pdf_entrada.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row1, text="Procurar", width=90,
                      command=self._escolher_pdf_entrada).pack(side="left", padx=(5, 0))

        ctk.CTkLabel(pdf_frame, text="Salvar PDF assinado em:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        row2 = ctk.CTkFrame(pdf_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(5, 10))
        self.entry_pdf_saida = ctk.CTkEntry(row2)
        self.entry_pdf_saida.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row2, text="Procurar", width=90,
                      command=self._escolher_pdf_saida).pack(side="left", padx=(5, 0))

        # ----- Tipo de certificado -----
        cert_frame = ctk.CTkFrame(container)
        cert_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(cert_frame, text="Certificado Digital", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        tipo_row = ctk.CTkFrame(cert_frame, fg_color="transparent")
        tipo_row.pack(fill="x", padx=10)
        ctk.CTkRadioButton(tipo_row, text="A1 (arquivo .pfx/.p12)", variable=self.tipo_certificado,
                           value="A1", command=self._atualizar_tipo_certificado).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(tipo_row, text="A3 (token/cartão)", variable=self.tipo_certificado,
                           value="A3", command=self._atualizar_tipo_certificado).pack(side="left")

        # --- A1 ---
        self.frame_a1 = ctk.CTkFrame(cert_frame, fg_color="gray20")
        ctk.CTkLabel(self.frame_a1, text="Arquivo do certificado (.pfx/.p12):").pack(anchor="w", padx=10, pady=(10, 0))
        row_a1 = ctk.CTkFrame(self.frame_a1, fg_color="transparent")
        row_a1.pack(fill="x", padx=10, pady=5)
        self.entry_pfx = ctk.CTkEntry(row_a1)
        self.entry_pfx.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row_a1, text="Procurar", width=90,
                      command=self._escolher_pfx).pack(side="left", padx=(5, 0))

        ctk.CTkLabel(self.frame_a1, text="Senha do certificado:").pack(anchor="w", padx=10, pady=(5, 0))
        self.entry_senha_a1 = ctk.CTkEntry(self.frame_a1, show="•")
        self.entry_senha_a1.pack(fill="x", padx=10, pady=(5, 10))

        # --- A3 ---
        self.frame_a3 = ctk.CTkFrame(cert_frame, fg_color="gray20")
        ctk.CTkLabel(self.frame_a3, text="Biblioteca PKCS#11 do fabricante (.dll/.so):").pack(anchor="w", padx=10, pady=(10, 0))
        row_a3 = ctk.CTkFrame(self.frame_a3, fg_color="transparent")
        row_a3.pack(fill="x", padx=10, pady=5)
        self.entry_pkcs11 = ctk.CTkEntry(row_a3)
        self.entry_pkcs11.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row_a3, text="Procurar", width=90,
                      command=self._escolher_pkcs11).pack(side="left", padx=(5, 0))

        ctk.CTkLabel(self.frame_a3, text="PIN do token:").pack(anchor="w", padx=10, pady=(5, 0))
        self.entry_pin_a3 = ctk.CTkEntry(self.frame_a3, show="•")
        self.entry_pin_a3.pack(fill="x", padx=10, pady=5)

        row_cert_a3 = ctk.CTkFrame(self.frame_a3, fg_color="transparent")
        row_cert_a3.pack(fill="x", padx=10, pady=(0, 10))
        self.combo_cert_a3 = ctk.CTkComboBox(row_cert_a3, values=[])
        self.combo_cert_a3.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row_cert_a3, text="Listar Certificados", width=140,
                      command=self._listar_certificados_a3).pack(side="left", padx=(5, 0))

        self._atualizar_tipo_certificado()

        ctk.CTkButton(cert_frame, text="Verificar Certificado", fg_color="gray40",
                      command=self._verificar_certificado).pack(padx=10, pady=(0, 5), anchor="w")

        self.label_profissional = ctk.CTkLabel(
            cert_frame, text="Nenhum certificado verificado ainda.",
            text_color="gray", font=("Arial", 10), justify="left", wraplength=560
        )
        self.label_profissional.pack(padx=10, pady=(0, 10), anchor="w")

        # ----- Assinatura visível -----
        vis_frame = ctk.CTkFrame(container)
        vis_frame.pack(fill="x", pady=(0, 15))

        self.var_visivel = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(vis_frame, text="Assinatura visível (com carimbo na página)",
                        variable=self.var_visivel, command=self._atualizar_visivel).pack(anchor="w", padx=10, pady=(10, 5))

        self.frame_visivel = ctk.CTkFrame(vis_frame, fg_color="gray20")
        self.frame_visivel.pack(fill="x", padx=10, pady=(0, 10))

        grid = ctk.CTkFrame(self.frame_visivel, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=10)
        for c in range(4):
            grid.grid_columnconfigure(c, weight=1)

        def campo(label, row, col, default=""):
            ctk.CTkLabel(grid, text=label, font=("Arial", 10)).grid(row=row * 2, column=col, sticky="w", padx=5)
            entry = ctk.CTkEntry(grid, width=100)
            entry.insert(0, default)
            entry.grid(row=row * 2 + 1, column=col, sticky="ew", padx=5, pady=(0, 8))
            return entry

        self.entry_pagina = campo("Página", 0, 0, "1")
        self.entry_x = campo("X", 0, 1, "100")
        self.entry_y = campo("Y", 0, 2, "100")
        self.entry_altura = campo("Altura", 0, 3, "90")
        self.entry_largura = campo("Largura", 1, 0, "260")
        self.entry_motivo = campo("Motivo (metadado)", 1, 1, "Aprovação")
        self.entry_localizacao = campo("Localização (metadado)", 1, 2, "")

        ctk.CTkLabel(
            self.frame_visivel,
            text=("O carimbo exibido no PDF traz Nome e CPF extraídos do certificado digital, e "
                  "Profissão/Conselho de Classe do profissional atualmente logado "
                  "(fonte Verdana 10, cor #002060)."),
            font=("Arial", 9, "italic"), text_color="gray", justify="left", wraplength=560
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # ----- Ações -----
        acoes_frame = ctk.CTkFrame(container, fg_color="transparent")
        acoes_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(acoes_frame, text="Assinar PDF", fg_color="green", height=40,
                      font=("Arial", 13, "bold"), command=self._assinar).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(acoes_frame, text="Validar Assinatura de um PDF", fg_color="blue",
                      command=self._validar).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(acoes_frame, text="Fechar", fg_color="darkgray",
                      command=self._on_close).pack(fill="x")

    def _atualizar_tipo_certificado(self):
        if self.tipo_certificado.get() == "A1":
            self.frame_a3.pack_forget()
            self.frame_a1.pack(fill="x", padx=10, pady=(0, 10))
        else:
            self.frame_a1.pack_forget()
            self.frame_a3.pack(fill="x", padx=10, pady=(0, 10))

    def _atualizar_visivel(self):
        if self.var_visivel.get():
            self.frame_visivel.pack(fill="x", padx=10, pady=(0, 10))
        else:
            self.frame_visivel.pack_forget()

    # ------------------------------------------------------------------
    # Seleção de arquivos
    # ------------------------------------------------------------------

    def _escolher_pdf_entrada(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar PDF", initialdir=self.pasta_inicial,
            filetypes=[("Arquivos PDF", "*.pdf")])
        if caminho:
            self.entry_pdf_entrada.delete(0, "end")
            self.entry_pdf_entrada.insert(0, caminho)
            self._sugerir_saida(caminho)

    def _sugerir_saida(self, caminho_entrada: str):
        base, ext = os.path.splitext(caminho_entrada)
        sugestao = f"{base}_assinado{ext}"
        self.entry_pdf_saida.delete(0, "end")
        self.entry_pdf_saida.insert(0, sugestao)

    def _escolher_pdf_saida(self):
        caminho = filedialog.asksaveasfilename(
            title="Salvar PDF assinado como", initialdir=self.pasta_inicial,
            defaultextension=".pdf", filetypes=[("Arquivos PDF", "*.pdf")])
        if caminho:
            self.entry_pdf_saida.delete(0, "end")
            self.entry_pdf_saida.insert(0, caminho)

    def _escolher_pfx(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar certificado A1",
            filetypes=[("Certificado PFX/P12", "*.pfx *.p12")])
        if caminho:
            self.entry_pfx.delete(0, "end")
            self.entry_pfx.insert(0, caminho)
            salvar_ultimo_pfx(caminho)

    def _escolher_pkcs11(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar biblioteca PKCS#11 do fabricante do token",
            filetypes=[("Biblioteca", "*.dll *.so")])
        if caminho:
            self.entry_pkcs11.delete(0, "end")
            self.entry_pkcs11.insert(0, caminho)

    # ------------------------------------------------------------------
    # Carregamento de certificado
    # ------------------------------------------------------------------

    def _carregar_certificado(self) -> bool:
        try:
            if self.tipo_certificado.get() == "A1":
                caminho_pfx = self.entry_pfx.get().strip()
                senha = self.entry_senha_a1.get()
                if not caminho_pfx or not senha:
                    messagebox.showwarning("Aviso", "Informe o arquivo do certificado e a senha.")
                    return False
                self.assinador.carregar_certificado_a1(caminho_pfx, senha)
                salvar_ultimo_pfx(caminho_pfx)
            else:
                caminho_lib = self.entry_pkcs11.get().strip()
                pin = self.entry_pin_a3.get()
                cert_label = self.combo_cert_a3.get().strip() or None
                if not caminho_lib or not pin:
                    messagebox.showwarning("Aviso", "Informe a biblioteca PKCS#11 e o PIN do token.")
                    return False
                self.assinador.carregar_certificado_a3(caminho_lib, pin, cert_label=cert_label)
            return True
        except SenhaIncorretaError as exc:
            messagebox.showerror("Senha incorreta", str(exc))
        except TokenNaoDetectadoError as exc:
            messagebox.showerror("Token não detectado", str(exc))
        except CertificadoInvalidoError as exc:
            messagebox.showerror("Certificado inválido", str(exc))
        except (FileNotFoundError, ImportError) as exc:
            messagebox.showerror("Erro", str(exc))
        except Exception as exc:
            messagebox.showerror("Erro ao carregar certificado", str(exc))
        return False

    def _listar_certificados_a3(self):
        caminho_lib = self.entry_pkcs11.get().strip()
        pin = self.entry_pin_a3.get()
        if not caminho_lib or not pin:
            messagebox.showwarning("Aviso", "Informe a biblioteca PKCS#11 e o PIN do token.")
            return
        try:
            rotulos = self.assinador.listar_certificados_a3(caminho_lib, pin)
            if not rotulos:
                messagebox.showinfo("Certificados", "Nenhum certificado encontrado no token.")
                return
            self.combo_cert_a3.configure(values=rotulos)
            self.combo_cert_a3.set(rotulos[0])
        except SenhaIncorretaError as exc:
            messagebox.showerror("PIN incorreto", str(exc))
        except TokenNaoDetectadoError as exc:
            messagebox.showerror("Token não detectado", str(exc))
        except (FileNotFoundError, ImportError) as exc:
            messagebox.showerror("Erro", str(exc))
        except Exception as exc:
            messagebox.showerror("Erro ao listar certificados", str(exc))
        finally:
            self.assinador.fechar_token()

    def _verificar_certificado(self):
        if not self._carregar_certificado():
            return
        try:
            info = self.assinador.informacoes_certificado()
            mensagem = (
                f"Titular: {info['titular']}\n"
                f"Emissor: {info['emissor']}\n"
                f"Nº de Série: {info['numero_serie']}\n"
                f"Válido de {info['valido_de']} até {info['valido_ate']}"
            )
            messagebox.showinfo("Informações do Certificado", mensagem)
            self._atualizar_status_profissional()
        except CertificadoInvalidoError as exc:
            messagebox.showerror("Certificado inválido", str(exc))
        finally:
            self.assinador.fechar_token()

    def _atualizar_status_profissional(self):
        """Mostra o nome/CPF extraídos do certificado e a profissão/conselho do profissional logado."""
        try:
            nome_cert = self.assinador.nome_titular_certificado()
        except CertificadoInvalidoError:
            nome_cert = None
        cpf_cert = self.assinador.extrair_cpf_certificado()

        profissao = self.current_user.get('profissao', '').strip()
        conselho = f"{self.current_user.get('sigla_conselho', '')} {self.current_user.get('inscricao', '')}".strip()

        if not self.current_user:
            aviso_profissional = "⚠ Nenhum profissional logado: Profissão/Conselho ficarão em branco no carimbo."
            cor = "orange"
        elif not profissao and not conselho:
            aviso_profissional = f"⚠ Profissional logado ({self.current_user.get('apelido', '')}) não tem Profissão/Conselho cadastrados."
            cor = "orange"
        else:
            aviso_profissional = f"✓ Profissão/Conselho serão do profissional logado: {profissao} - {conselho}"
            cor = "green"

        self.label_profissional.configure(
            text=(f"Certificado: {nome_cert or '?'} "
                  f"(CPF: {cpf_cert or 'não identificado'})\n{aviso_profissional}"),
            text_color=cor
        )

    # ------------------------------------------------------------------
    # Assinatura / Validação
    # ------------------------------------------------------------------

    def _assinar(self):
        pdf_entrada = self.entry_pdf_entrada.get().strip()
        pdf_saida = self.entry_pdf_saida.get().strip()

        if not pdf_entrada or not os.path.exists(pdf_entrada):
            messagebox.showwarning("Aviso", "Selecione um PDF válido para assinar.")
            return
        if not pdf_saida:
            messagebox.showwarning("Aviso", "Informe onde salvar o PDF assinado.")
            return

        if not self._carregar_certificado():
            return

        try:
            self._atualizar_status_profissional()

            dados_signatario = {
                'nome': self.assinador.nome_titular_certificado(),
                'cpf': self.assinador.extrair_cpf_certificado() or '',
                'profissao': self.current_user.get('profissao', '').strip(),
                'conselho': f"{self.current_user.get('sigla_conselho', '')} {self.current_user.get('inscricao', '')}".strip(),
            }

            config_visual = None
            if self.var_visivel.get():
                config_visual = ConfiguracaoAssinaturaVisivel(
                    pagina=int(self.entry_pagina.get() or 1),
                    x=float(self.entry_x.get() or 100),
                    y=float(self.entry_y.get() or 100),
                    largura=float(self.entry_largura.get() or 260),
                    altura=float(self.entry_altura.get() or 90),
                )

            self.assinador.assinar(
                pdf_entrada, pdf_saida,
                visivel=self.var_visivel.get(),
                config_visual=config_visual,
                dados_signatario=dados_signatario,
                motivo=self.entry_motivo.get().strip(),
                localizacao=self.entry_localizacao.get().strip(),
            )
            messagebox.showinfo("Sucesso", f"PDF assinado com sucesso:\n{pdf_saida}")
        except CertificadoInvalidoError as exc:
            messagebox.showerror("Certificado inválido", str(exc))
        except Exception as exc:
            messagebox.showerror("Erro ao assinar PDF", str(exc))
        finally:
            self.assinador.fechar_token()

    def _validar(self):
        pdf_path = filedialog.askopenfilename(
            title="Selecionar PDF para validar", initialdir=self.pasta_inicial,
            filetypes=[("Arquivos PDF", "*.pdf")])
        if not pdf_path:
            return

        try:
            from models.assinatura_digital import AssinadorPDF as _Assinador
            resultados = _Assinador.validar_assinatura(pdf_path)
        except Exception as exc:
            messagebox.showerror("Erro ao validar", str(exc))
            return

        linhas = []
        for r in resultados:
            if not r.get("assinado"):
                linhas.append(r.get("mensagem", "PDF não assinado."))
                continue
            if "erro" in r:
                linhas.append(f"Campo {r.get('campo')}: erro ao validar ({r['erro']})")
                continue
            linhas.append(
                f"Campo: {r['campo']}\n"
                f"  Íntegro: {'Sim' if r['integro'] else 'NÃO'}\n"
                f"  Válido criptograficamente: {'Sim' if r['valido_criptograficamente'] else 'NÃO'}\n"
                f"  Cadeia confiável (requer raiz ICP-Brasil configurada): {r['cadeia_confiavel']}\n"
                f"  Titular: {r['titular']}\n"
                f"  Emissor: {r['emissor']}\n"
                f"  Assinado em: {r['assinado_em']}"
            )

        messagebox.showinfo("Resultado da Validação", "\n\n".join(linhas))

    def _on_close(self):
        self.assinador.fechar_token()
        self.destroy()
