# Changelog

## [Unreleased]
- Repositório criado no GitHub: https://github.com/AdilsonPeginiJunior/escrituracao-carne-leao
- Adicionado `.gitignore` para ignorar arquivos gerados e ambientes virtuais
- Removidos arquivos de cache Python (`__pycache__`, `.pyc`) e arquivo de verificação gerado
- Atualizado `README.md` com link do repositório
- Adicionado campo `fim` no cadastro de pacientes e carregamento em edição
- Permitir valores de template no campo `gera_relatorio` (templates com underscore)
- Gerador de relatórios: inclusão de `#DtFimAtend`, `#DtInicioAtend` refinado e regex de extração de datas
- Correções de gramática/tempo verbal no texto de sessões (singular/plural e futuras)
- Relatórios salvos em pastas mensais na Área de Trabalho (`Relatório de {Mês}`)
- Adicionado `generate_for_adrielle.py` para geração de exemplo e testes locais
