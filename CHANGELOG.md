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
- Estrutura de dados reorganizada por profissional em `profissionais/<apelido>/`
- Script de apoio renomeado para `gerar_relatorio_por_profissional.py` para refletir o uso real
- Dados de pacientes, despesas e recibos agora ficam dentro da pasta do profissional logado
- Adicionada assinatura digital de PDFs com certificados ICP-Brasil A1 (.pfx/.p12) e A3 (token/cartão PKCS#11) via `pyHanko` (`models/assinatura_digital.py`, `ui/assinatura_digital.py`), com suporte a assinatura visível/invisível e validação de assinaturas
- Cadastro de profissionais: adicionados campos Profissão, Sigla do Conselho e reorganizado CPF/Nº de Inscrição no Conselho
- Assinatura digital: carimbo visível agora busca automaticamente Nome, CPF, Profissão e Conselho de Classe do profissional cadastrado cujo CPF corresponda ao do certificado, formatado em Verdana 10 cor #002060
