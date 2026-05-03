# Gerador de Relatórios - Documentação

## Visão Geral

O gerador de relatórios automatiza a criação de documentos PDF a partir de recibos de saúde, preenchendo automaticamente um template do Word com dados do paciente, profissional e consultas realizadas.

## Funcionalidades

### Extração Automática de Dados

O sistema extrai automaticamente as seguintes informações do recibo:

| Variável | Fonte | Descrição |
|----------|-------|-----------|
| `#NomePac` | Cadastro de pacientes | Nome do beneficiário (ou pagador se não houver beneficiário) |
| `#CPF` | Recibo | CPF do beneficiário (ou pagador) |
| `#DtInicioAtend` | Cadastro de pacientes | Data de início do atendimento |
| `#NrSessoes` | Descrição do recibo | Número de sessões (extraído via regex) |
| `#DataDasCons` | Descrição do recibo | Lista formatada de datas das consultas |
| `#UltDiaMesConsultas` | Cálculo automático | Último dia do mês da primeira consulta |
| `#MesDasConsultas2` | Cálculo automático | Mês por extenso da primeira consulta |
| `#AnoDasConsultas2` | Cálculo automático | Ano da primeira consulta |
| `#FormaPresencial` | Configuração | Vazio por padrão (espaço em branco) |

### Regras de Beneficiário

Se o campo `cpf_benef` no cadastro de pacientes for **diferente e não vazio** comparado ao `cpf_pagador`:
- Usa `nome_benef` para `#NomePac`
- Usa `cpf_benef` para `#CPF`
- Usa `inicio` equivalente ao `cpf_benef`

Caso contrário, usa dados do pagador.

## Como Usar

### 1. Preparar o Template

1. Crie ou edite um arquivo `.docx` com as variáveis que deseja substituir
2. Coloque o arquivo na pasta `modelosRelatorios/`
3. O padrão é usar `RelatorioTemplateCarimboFem.docx`

**Exemplo de template:**
```
Relatório de Atendimento

Paciente: #NomePac
CPF: #CPF
Início do Atendimento: #DtInicioAtend
Número de Sessões: #NrSessoes
Datas das Consultas: #DataDasCons
Ultimo dia do mês: #UltDiaMesConsultas
Mês: #MesDasConsultas2
Ano: #AnoDasConsultas2
Forma: #FormaPresencial
```

### 2. Usar na Aplicação

1. Abra a aplicação Carnê Leão
2. Vá para a aba **"Receita Saúde"**
3. Clique no botão **"Gerar Relatórios"** (azul escuro)
4. A janela de geração de relatórios abrirá

### 3. Gerar Relatório

Na janela de relatórios:

1. A lista à esquerda mostra todos os recibos disponíveis
2. Clique em **"Selecionar"** para escolher um recibo
3. Os detalhes aparecem à direita com preview das variáveis
4. (Opcional) Clique em **"Escolher Pasta"** para mudar o local de saída
5. Clique em **"Gerar Relatório"** para criar o PDF

### 4. Localizar o Arquivo

O PDF será salvo com o nome:
```
{Nome_Beneficiario} - Relatório {Ano}{Mês}.pdf
```

**Exemplo:**
```
Ana Paula Costa Xavier - Relatório 2026abril.pdf
```

## Estrutura Técnica

### Módulos

#### `models/report_generator.py`

**Classes principais:**

- **`ReportDataExtractor`**: Extrai dados da descrição do recibo e do cadastro de pacientes
  - `extract_sessions_from_description()`: Extrai número de sessões usando regex
  - `extract_dates_from_description()`: Extrai datas das consultas
  - `extract_report_variables()`: Extrai todas as variáveis do relatório

- **`ReportGenerator`**: Gera os documentos
  - `generate_report()`: Cria relatório DOCX e converte para PDF
  - `replace_text_in_document()`: Substitui variáveis no documento
  - `convert_docx_to_pdf()`: Converte DOCX para PDF usando LibreOffice

- **`RecibosReportManager`**: Gerenciador de relatórios
  - Coordena acesso aos dados de recibos e pacientes
  - Procura dados em arquivos JSON de profissionais

#### `ui/relatorios.py`

**Classe:**

- **`GerarRelatoriosWindow`**: Interface gráfica para geração de relatórios
  - Lista de recibos disponíveis
  - Preview de variáveis extraídas
  - Seleção de pasta de saída
  - Botões para gerar relatórios

## Dependências

As seguintes bibliotecas foram adicionadas ao `requirements.txt`:

```
python-docx>=0.8.11       # Manipulação de arquivos DOCX
pdf2docx>=0.5.1           # Conversão de PDF para DOCX
reportlab>=3.6.0          # Geração de PDF
pypdf>=3.0.0              # Manipulação de PDF
```

Além disso, o sistema usa **LibreOffice** via linha de comando para converter DOCX para PDF. O sistema detecta a instalação automaticamente.

## Extração de Dados da Descrição

### Número de Sessões

O sistema procura por padrões como:
- "04 sessões"
- "01 sessão"
- "09 sessões"

**Regex:** `r'(\d+)\s+sess(?:ões|ão)'`

### Datas das Consultas

O sistema procura por datas no formato `DD/MM/YYYY`:
- "06/04/2026, 13/04/2026, 20/04/2026 e 27/04/2026"

**Regex:** `r'(\d{2}/\d{2}/\d{4})'`

A primeira data é usada para calcular o último dia do mês e o mês/ano do relatório.

## Tratamento de Erros

O sistema trata os seguintes cenários:

1. **Template não encontrado**: Mensagem de erro exibida
2. **Paciente não encontrado**: Mensagem de aviso, relatório não gerado
3. **LibreOffice não instalado**: Fallback para `docx2pdf` (se disponível)
4. **Arquivo DOCX inválido**: Mensagem de erro

## Melhorias Futuras

- [ ] Adicionar campo "QtdSessoes" ao arquivo de recibos
- [ ] Adicionar campo "DataDasCons" ao arquivo de recibos
- [ ] Suporte a múltiplos templates
- [ ] Geração em lote de vários relatórios
- [ ] Suporte a PDF/A para conformidade fiscal

## Testes

Execute o teste de validação com:

```bash
python test_report_generator.py
```

O teste valida:
- Extração de número de sessões
- Extração de datas
- Cálculo de último dia do mês
- Formatação de variáveis
- Tratamento de beneficiários

## Troubleshooting

### "LibreOffice não encontrado"

**Solução:** Instale LibreOffice na máquina:
- Windows: Baixe em https://www.libreoffice.org/download/
- Linux: `sudo apt-get install libreoffice`
- Mac: `brew install libreoffice`

### "Paciente não encontrado"

**Solução:** Verifique se:
1. O paciente está cadastrado no sistema
2. O CPF no recibo corresponde ao CPF no cadastro de pacientes
3. O arquivo `{profissional}_pacientes.json` existe e é válido

### "Variáveis não são substituídas corretamente"

**Solução:** Verifique se:
1. Os nomes das variáveis no template estão corretos (com `#` no início)
2. As variáveis não estão divididas entre diferentes runs do Word
3. O template é um arquivo DOCX válido (não ODP ou similar)

## Exemplo Completo

### Dados de Entrada

**Recibo:**
```json
{
  "data": "15/04/2026",
  "cpf_pagador": "39111825898",
  "cpf_benef": "39111825898",
  "descricao": "Referente a 04 sessões de psicoterapia realizadas nos dias 06/04/2026, 13/04/2026, 20/04/2026 e 27/04/2026."
}
```

**Paciente:**
```json
{
  "nome_pagador": "Ana Paula Costa Xavier",
  "cpf_pagador": "39111825898",
  "inicio": "26/10/2023"
}
```

### Variáveis Geradas

```
#NomePac = "Ana Paula Costa Xavier"
#CPF = "39111825898"
#DtInicioAtend = "26/10/2023"
#NrSessoes = "4"
#DataDasCons = "06/04/2026, 13/04/2026, 20/04/2026 e 27/04/2026"
#UltDiaMesConsultas = "30"
#MesDasConsultas2 = "abril"
#AnoDasConsultas2 = "2026"
#FormaPresencial = ""
```

### Arquivo Gerado

```
Ana Paula Costa Xavier - Relatório 2026abril.pdf
```
