import unittest
from unittest.mock import patch, MagicMock
from models.assinatura_digital import AssinadorPDF


class AssinaturaDigitalStrictTests(unittest.TestCase):
    @patch("models.assinatura_digital.os.path.exists", return_value=True)
    @patch("pyhanko.pdf_utils.incremental_writer.IncrementalPdfFileWriter")
    @patch("pyhanko.sign.fields.append_signature_field")
    @patch("pyhanko.sign.signers.PdfSigner")
    def test_assinar_passes_strict_false(
        self, mock_pdf_signer, mock_append_field, mock_writer_cls, mock_exists
    ):
        assinador = AssinadorPDF()
        assinador._signer = MagicMock()

        mock_writer = MagicMock()
        mock_writer_cls.return_value = mock_writer

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"%PDF-1.4")):
            assinador.assinar("entrada.pdf", "saida.pdf", visivel=False)

        # Verifica se o IncrementalPdfFileWriter foi chamado com strict=False
        args, kwargs = mock_writer_cls.call_args
        self.assertEqual(kwargs.get("strict"), False)

    @patch("models.assinatura_digital.os.path.exists", return_value=True)
    @patch("pyhanko.pdf_utils.reader.PdfFileReader")
    def test_validar_assinatura_passes_strict_false(self, mock_reader_cls, mock_exists):
        mock_reader = MagicMock()
        mock_reader.embedded_signatures = []
        mock_reader_cls.return_value = mock_reader

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"%PDF-1.4")):
            resultado = AssinadorPDF.validar_assinatura("doc.pdf")

        args, kwargs = mock_reader_cls.call_args
        self.assertEqual(kwargs.get("strict"), False)
        self.assertFalse(resultado[0]["assinado"])


if __name__ == "__main__":
    unittest.main()
