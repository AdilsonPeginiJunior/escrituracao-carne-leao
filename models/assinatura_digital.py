"""Assinatura e validação de PDFs com certificados ICP-Brasil (A1 e A3) via pyHanko.

Suporta:
- A1: certificado em arquivo .pfx/.p12 protegido por senha.
- A3: certificado em token/cartão criptográfico via PKCS#11.
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "config_assinatura_digital.json")


def salvar_ultimo_pfx(caminho: str) -> None:
    """Persiste o caminho do último certificado .pfx/.p12 selecionado pelo usuário."""
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"ultimo_pfx": caminho}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar último certificado selecionado: {e}")


def carregar_ultimo_pfx() -> Optional[str]:
    """Retorna o caminho do último certificado .pfx/.p12 selecionado, se houver."""
    try:
        if os.path.exists(_CONFIG_PATH):
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("ultimo_pfx")
    except Exception as e:
        print(f"Erro ao carregar último certificado selecionado: {e}")
    return None


class CertificadoInvalidoError(Exception):
    """Certificado expirado, corrompido ou não encontrado."""


class SenhaIncorretaError(Exception):
    """Senha do certificado (.pfx) ou PIN do token incorretos."""


class TokenNaoDetectadoError(Exception):
    """Token/cartão A3 ou biblioteca PKCS#11 não encontrados."""


@dataclass
class ConfiguracaoAssinaturaVisivel:
    """Parâmetros de posicionamento da assinatura visível na página."""
    pagina: int = 1
    x: float = 100
    y: float = 100
    largura: float = 260
    altura: float = 90


# Estilo fixo do carimbo de assinatura (Verdana 10, cor #002060).
_COR_CARIMBO_HEX = "#002060"
_TAMANHO_FONTE_CARIMBO = 10
_CAMINHOS_VERDANA = (
    r"C:\Windows\Fonts\verdana.ttf",
    r"C:\Windows\Fonts\Verdana.ttf",
)


def _hex_para_rgb01(hex_color: str):
    """Converte uma cor hexadecimal (#RRGGBB) para uma tupla RGB entre 0 e 1."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _fonte_verdana_factory():
    """Tenta carregar a fonte Verdana do sistema; retorna None se indisponível."""
    for caminho in _CAMINHOS_VERDANA:
        if os.path.exists(caminho):
            try:
                from pyhanko.pdf_utils.font import opentype
                return opentype.GlyphAccumulatorFactory(caminho)
            except Exception:
                return None
    return None


def _formatar_nome_titulo(nome: str) -> str:
    """Formata um nome em Title Case, mantendo preposições em minúsculas."""
    preposicoes = {"de", "da", "do", "das", "dos", "e"}
    palavras = nome.strip().lower().split()
    if not palavras:
        return nome
    resultado = [palavras[0].capitalize()]
    resultado.extend(
        p if p in preposicoes else p.capitalize() for p in palavras[1:]
    )
    return " ".join(resultado)


def _formatar_cpf(cpf: str) -> str:
    """Formata um CPF (somente dígitos) para o padrão 000.000.000-00."""
    digitos = ''.join(filter(str.isdigit, str(cpf)))
    if len(digitos) != 11:
        return cpf
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


class AssinadorPDF:
    """Carrega um certificado ICP-Brasil (A1 ou A3) e assina/valida arquivos PDF."""

    def __init__(self):
        self._signer = None
        self._pkcs11_session = None

    # ---------------------------------------------------------------
    # Carregamento de certificados
    # ---------------------------------------------------------------

    def carregar_certificado_a1(self, caminho_pfx: str, senha: str):
        """Carrega um certificado A1 a partir de um arquivo .pfx/.p12."""
        from pyhanko.sign import signers

        if not os.path.exists(caminho_pfx):
            raise FileNotFoundError(
                f"Arquivo de certificado não encontrado: {caminho_pfx}")

        try:
            signer = signers.SimpleSigner.load_pkcs12(
                pfx_file=caminho_pfx,
                passphrase=senha.encode("utf-8"),
            )
        except Exception as exc:
            mensagem = str(exc).lower()
            if any(termo in mensagem for termo in ("mac", "password", "decrypt", "invalid password")):
                raise SenhaIncorretaError(
                    "Senha do certificado incorreta.") from exc
            raise CertificadoInvalidoError(
                f"Não foi possível carregar o certificado: {exc}") from exc

        if signer is None:
            raise CertificadoInvalidoError("Certificado inválido ou corrompido.")

        self._signer = signer
        self._validar_vigencia_certificado()
        return self._signer

    def carregar_certificado_a3(self, caminho_biblioteca_pkcs11: str, pin: str,
                                 cert_label: Optional[str] = None,
                                 slot_no: Optional[int] = None):
        """Carrega um certificado A3 de um token/cartão via PKCS#11."""
        try:
            from pyhanko.sign.pkcs11 import PKCS11Signer, open_pkcs11_session
        except ImportError as exc:
            raise ImportError(
                "Suporte a A3 requer as dependências opcionais: "
                "pip install pyHanko[pkcs11]"
            ) from exc

        if not os.path.exists(caminho_biblioteca_pkcs11):
            raise FileNotFoundError(
                "Biblioteca PKCS#11 (.dll/.so) do fabricante do token não "
                f"encontrada: {caminho_biblioteca_pkcs11}"
            )

        try:
            self._pkcs11_session = open_pkcs11_session(
                lib_location=caminho_biblioteca_pkcs11,
                slot_no=slot_no,
                user_pin=pin,
            )
        except Exception as exc:
            mensagem = str(exc).lower()
            if "pin" in mensagem:
                raise SenhaIncorretaError("PIN do token incorreto.") from exc
            raise TokenNaoDetectadoError(
                f"Token/cartão não detectado ou biblioteca inválida: {exc}"
            ) from exc

        try:
            signer = PKCS11Signer(
                pkcs11_session=self._pkcs11_session,
                cert_label=cert_label,
                key_label=cert_label,
            )
        except Exception as exc:
            self.fechar_token()
            raise CertificadoInvalidoError(
                f"Não foi possível localizar o certificado no token: {exc}") from exc

        self._signer = signer
        self._validar_vigencia_certificado()
        return self._signer

    def listar_certificados_a3(self, caminho_biblioteca_pkcs11: str, pin: str,
                                 slot_no: Optional[int] = None) -> list:
        """Lista os rótulos (labels) de certificados disponíveis no token PKCS#11."""
        try:
            from pyhanko.sign.pkcs11 import open_pkcs11_session
            import pkcs11 as pkcs11_lib
        except ImportError as exc:
            raise ImportError(
                "Suporte a A3 requer as dependências opcionais: "
                "pip install pyHanko[pkcs11]"
            ) from exc

        if not os.path.exists(caminho_biblioteca_pkcs11):
            raise FileNotFoundError(
                f"Biblioteca PKCS#11 não encontrada: {caminho_biblioteca_pkcs11}")

        session = open_pkcs11_session(
            lib_location=caminho_biblioteca_pkcs11, slot_no=slot_no, user_pin=pin
        )
        try:
            rotulos = []
            for obj in session.get_objects({pkcs11_lib.Attribute.CLASS: pkcs11_lib.ObjectClass.CERTIFICATE}):
                if obj.label:
                    rotulos.append(obj.label)
            return rotulos
        finally:
            session.close()

    def fechar_token(self):
        """Encerra a sessão com o token A3, garantindo que não fique aberta após o uso."""
        if self._pkcs11_session is not None:
            try:
                self._pkcs11_session.close()
            finally:
                self._pkcs11_session = None

    def _validar_vigencia_certificado(self):
        cert = self._signer.signing_cert
        agora = datetime.now(timezone.utc)
        if cert.not_valid_after < agora:
            raise CertificadoInvalidoError(
                f"O certificado expirou em {cert.not_valid_after:%d/%m/%Y}.")
        if cert.not_valid_before > agora:
            raise CertificadoInvalidoError("O certificado ainda não está vigente.")

    def nome_titular_certificado(self) -> str:
        """Extrai o nome do titular do certificado (Common Name), formatado sem caixa alta."""
        if self._signer is None:
            raise CertificadoInvalidoError("Nenhum certificado carregado.")
        cert = self._signer.signing_cert
        cn = ''
        try:
            cn = cert.subject.native.get('common_name', '') or ''
        except Exception:
            pass
        if ':' in cn:
            # Padrão comum de e-CPF: Common Name no formato "NOME:CPF".
            cn = cn.split(':')[0]
        if not cn:
            cn = cert.subject.human_friendly
        return _formatar_nome_titulo(cn)

    def informacoes_certificado(self) -> dict:
        """Retorna dados do certificado carregado (emissor, titular, validade)."""
        if self._signer is None:
            raise CertificadoInvalidoError("Nenhum certificado carregado.")
        cert = self._signer.signing_cert
        return {
            "titular": cert.subject.human_friendly,
            "emissor": cert.issuer.human_friendly,
            "numero_serie": str(cert.serial_number),
            "valido_de": cert.not_valid_before.strftime("%d/%m/%Y"),
            "valido_ate": cert.not_valid_after.strftime("%d/%m/%Y"),
        }

    def extrair_cpf_certificado(self) -> Optional[str]:
        """Tenta extrair o CPF do titular do certificado ICP-Brasil carregado (best-effort)."""
        if self._signer is None:
            return None
        cert = self._signer.signing_cert

        # Padrão comum de e-CPF: Common Name no formato "NOME:CPF".
        try:
            cn = cert.subject.native.get('common_name', '') or ''
            if ':' in cn:
                digitos = ''.join(filter(str.isdigit, cn.split(':')[-1]))
                if len(digitos) == 11:
                    return digitos
        except Exception:
            pass

        # SubjectAltName otherName ICP-Brasil (OID 2.16.76.1.3.1 - Pessoa Física).
        try:
            san = cert.subject_alt_name_value
            if san:
                for nome_alt in san:
                    if nome_alt.name != 'other_name':
                        continue
                    if nome_alt.chosen['type_id'].dotted != '2.16.76.1.3.1':
                        continue
                    valor = nome_alt.chosen['value'].parsed.native
                    if isinstance(valor, bytes):
                        valor = valor.decode('latin-1', errors='ignore')
                    digitos = ''.join(filter(str.isdigit, str(valor)))
                    if len(digitos) >= 19:
                        return digitos[8:19]
                    if len(digitos) == 11:
                        return digitos
        except Exception:
            pass

        return None

    # ---------------------------------------------------------------
    # Assinatura
    # ---------------------------------------------------------------

    def assinar(self, caminho_pdf_entrada: str, caminho_pdf_saida: str,
                visivel: bool = True,
                config_visual: Optional[ConfiguracaoAssinaturaVisivel] = None,
                dados_signatario: Optional[dict] = None,
                motivo: str = "", localizacao: str = "") -> str:
        """Assina o PDF informado e salva o resultado em caminho_pdf_saida.

        `dados_signatario`, se informado, deve conter as chaves opcionais
        'nome', 'cpf', 'profissao' e 'conselho'; o carimbo visível é então
        renderizado em Verdana 10, cor #002060, no formato:
            Assinado digitalmente por: <nome>
            CPF: <cpf>
            Profissão: <profissao>
            Conselho de classe: <conselho>

        A assinatura é sempre adicionada como uma nova atualização incremental do
        PDF: assinaturas anteriores nunca são removidas ou sobrescritas.
        """
        from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
        from pyhanko.sign import signers, fields
        from pyhanko.sign.fields import SigFieldSpec, SigSeedSubFilter
        from pyhanko import stamp
        from pyhanko.pdf_utils import text

        if self._signer is None:
            raise CertificadoInvalidoError(
                "Nenhum certificado carregado. Chame carregar_certificado_a1/a3 primeiro.")

        if not os.path.exists(caminho_pdf_entrada):
            raise FileNotFoundError(f"PDF não encontrado: {caminho_pdf_entrada}")

        pasta_saida = os.path.dirname(os.path.abspath(caminho_pdf_saida))
        if pasta_saida:
            os.makedirs(pasta_saida, exist_ok=True)

        field_name = f"AssinaturaCarneLeao_{datetime.now():%Y%m%d%H%M%S}"

        with open(caminho_pdf_entrada, "rb") as doc:
            writer = IncrementalPdfFileWriter(doc)

            stamp_style = None
            cfg = config_visual or ConfiguracaoAssinaturaVisivel()

            if visivel:
                x0, y0 = cfg.x, cfg.y
                x1, y1 = cfg.x + cfg.largura, cfg.y + cfg.altura

                fields.append_signature_field(
                    writer,
                    sig_field_spec=SigFieldSpec(
                        field_name, on_page=cfg.pagina - 1, box=(x0, y0, x1, y1)
                    ),
                )

                if dados_signatario:
                    linhas = [
                        f"Assinado digitalmente por: {_formatar_nome_titulo(dados_signatario.get('nome', ''))}"
                    ]
                    if dados_signatario.get('cpf'):
                        linhas.append(f"CPF: {_formatar_cpf(dados_signatario['cpf'])}")
                    if dados_signatario.get('profissao'):
                        linhas.append(f"Profissão: {dados_signatario['profissao']}")
                    if dados_signatario.get('conselho'):
                        linhas.append(f"Conselho de classe: {dados_signatario['conselho']}")
                    texto = "\n".join(linhas)
                else:
                    texto = "Assinado digitalmente por: %(signer)s\nData: %(ts)s"

                estilo_texto_kwargs = {
                    "font_size": _TAMANHO_FONTE_CARIMBO,
                    "text_color": _hex_para_rgb01(_COR_CARIMBO_HEX),
                }
                fonte_verdana = _fonte_verdana_factory()
                if fonte_verdana is not None:
                    estilo_texto_kwargs["font"] = fonte_verdana

                stamp_style = stamp.TextStampStyle(
                    stamp_text=texto,
                    border_width=1,
                    text_box_style=text.TextBoxStyle(**estilo_texto_kwargs),
                )

            meta = signers.PdfSignatureMetadata(
                field_name=field_name,
                reason=motivo or None,
                location=localizacao or None,
                subfilter=SigSeedSubFilter.PADES,
            )

            pdf_signer = signers.PdfSigner(
                meta, signer=self._signer, stamp_style=stamp_style
            )

            with open(caminho_pdf_saida, "wb") as saida:
                pdf_signer.sign_pdf(writer, output=saida)

        return caminho_pdf_saida

    # ---------------------------------------------------------------
    # Validação
    # ---------------------------------------------------------------

    @staticmethod
    def validar_assinatura(caminho_pdf: str) -> list:
        """Verifica as assinaturas presentes em um PDF e retorna informações sobre cada uma."""
        from pyhanko.pdf_utils.reader import PdfFileReader
        from pyhanko.sign.validation import validate_pdf_signature

        if not os.path.exists(caminho_pdf):
            raise FileNotFoundError(f"PDF não encontrado: {caminho_pdf}")

        resultados = []
        with open(caminho_pdf, "rb") as f:
            reader = PdfFileReader(f)
            assinaturas = reader.embedded_signatures

            if not assinaturas:
                return [{"assinado": False, "mensagem": "O PDF não possui assinaturas digitais."}]

            for sig in assinaturas:
                try:
                    status = validate_pdf_signature(sig)
                    cert = sig.signer_cert
                    carimbo = getattr(sig, "self_reported_timestamp", None)
                    resultados.append({
                        "assinado": True,
                        "campo": sig.field_name,
                        # Integridade criptográfica do documento (byte-a-byte).
                        "integro": bool(status.intact),
                        "valido_criptograficamente": bool(status.valid),
                        # Requer certificados raiz ICP-Brasil configurados para ser conclusivo.
                        "cadeia_confiavel": getattr(status, "trusted", None),
                        "titular": cert.subject.human_friendly if cert else None,
                        "emissor": cert.issuer.human_friendly if cert else None,
                        "assinado_em": carimbo.strftime("%d/%m/%Y %H:%M") if carimbo else None,
                    })
                except Exception as exc:
                    resultados.append({
                        "assinado": True,
                        "campo": getattr(sig, "field_name", "?"),
                        "erro": str(exc),
                    })

        return resultados
