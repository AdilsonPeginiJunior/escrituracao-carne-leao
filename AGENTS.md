# Regras de manutenção

- Ao salvar relatórios, use sempre `Relatorio` (sem acento) nos nomes dos arquivos e das pastas de saída. Não reintroduza `Relatório` nesses caminhos em futuras alterações.
- Preserve essa regra na interface (`ui/relatorios.py`), no script `gerar_relatorio_por_profissional.py` e no gerador `models/report_generator.py`, inclusive em novos fluxos de exportação.
- Exemplos: `Relatorio de Maio/` e `Nome do Paciente - Relatorio 2026Maio.pdf`. Os textos exibidos na interface e o conteúdo dos documentos podem manter a acentuação normal.
