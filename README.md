# Sistema de Geração de CSV - Carnê Leão

Repositório GitHub: https://github.com/AdilsonPeginiJunior/escrituracao-carne-leao

Sistema em Python com interface gráfica (customtkinter) para geração de arquivos CSV de receita saúde e despesas profissionais, compatíveis com a importação no site da Receita Federal para profissionais de saúde.

## Recursos

- **Interface Gráfica Moderna**: Desenvolvido com customtkinter
- **Interface Responsiva**: Adapta-se automaticamente ao tamanho da tela (90% da largura, 85% da altura)
- **Gestão de Recibos**: Salvar, editar, deletar e exportar recibos de receita saúde
- **Gestão de Despesas**: Salvar, editar, deletar e exportar despesas profissionais
- **Persistência de Dados**: Recibos e despesas salvos em JSON local
- **Campos Fixos**: Código de receita, inscrição, tipo de pagador e CPF do profissional já preenchidos
- **Seletor de Data**: Calendário suspenso para seleção visual de datas
- **Seletor de Múltiplas Datas**: Calendário interativo para seleção de várias datas de sessões
- **Geração Automática de Descrição**: Gera automaticamente descrição com contagem de sessões (01, 02... 12+)
- **Exportação CSV**: Formato compatível com Receita Federal
- **Validação de Dados**: Validação automática com mensagens de erro detalhadas e verificação de CPF
- **Formatação Automática**: Campos de CPF formatados (000.000.000-00) nas listas visuais
- **Gestão de Pacientes**: Carregamento automático de CPFs a partir de `pacientes.json`
- **Interface Dual**: Formulário + Lista de itens salvos em cada aba com scroll automático
- **Scroll Dinâmico**: Formulários e listas com scrollbars para melhor navegação

## Requisitos

- Python 3.8+
- customtkinter 5.2.2

## Instalação

1. Clone ou baixe o projeto
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

Para iniciar a aplicação:

```bash
python app.py
```

### Abas da Aplicação

#### 1. Receita Saúde

**Painel Esquerdo - Novo Recibo:**
- Preencha o formulário com os dados do recibo
- Clique em **"Novo Recibo"** (azul) para iniciar um novo cadastro (limpa formulário)
- Clique em "Salvar Recibo" (verde) para armazenar

**Campos Fixos (Pré-preenchidos):**
- Código de Receita: R01.001.001
- Número de Inscrição: 06/23007
- Tipo de Pagador: PF (Pessoa Física)
- CNPJ/CPF Profissional: 08750012894

**Campos Editáveis:**
- Data de Pagto (dd/mm/aaaa) - obrigatório com seletor de calendário 📅
- Valor (R$) - obrigatório
- Descrição/Observações (Sessões) - Gerado automaticamente com seletor de múltiplas datas 📆
- **CPF Pagador** - Lista suspensa carregada de `pacientes.json` (formatação visual 000.000.000-00)
- **CPF do Beneficiário** - Lista suspensa com preenchimento automático baseado no pagador

**Painel Direito - Recibos Salvos:**
- Visualize todos os recibos já salvos
- Cada item exibe: Data, Valor e Descrição
- **Botão Editar**: Carrega o recibo no formulário para modificação
- **Botão Deletar**: Remove o recibo com confirmação
- **Botão Exportar**: Gera arquivo CSV com todos os recibos

#### 2. Despesas Profissionais

**Painel Esquerdo - Nova Despesa:**
- Preencha o formulário com os dados da despesa
- Clique em "Salvar Despesa" para armazenar
- Clique em "Limpar Formulário" para resetar

**Campos Obrigatórios:**
- Data de Pagto (dd/mm/aaaa) - com seletor de calendário 📅
- Código de Despesa
- Valor (R$)
- Descrição

**Campos Opcionais:**
- Valor Complementar
- Competência (mm/aaaa)

**Painel Direito - Despesas Salvas:**
- Visualize todas as despesas já salvas
- Cada item exibe: Data, Valor e Descrição
- **Botão Editar**: Carrega a despesa no formulário para modificação
- **Botão Deletar**: Remove a despesa com confirmação
- **Botão Exportar**: Gera arquivo CSV com todas as despesas

## Estrutura do Projeto

```
escrituracao-carne-leao/
├── app.py                    # Aplicação principal com interface gráfica
├── models/
│   ├── __init__.py
│   ├── receita_saude.py     # Gerenciador de receitas de saúde
│   ├── despesas.py          # Gerenciador de despesas profissionais
│   └── storage.py           # Persistência de dados em JSON
├── ui/
│   ├── __init__.py
│   └── widgets.py           # Componentes UI reutilizáveis
├── recibos_saude.json       # Arquivo de dados de recibos (auto-criado)
├── <apelido>_despesas_profissionais.json # Arquivo de dados de despesas por profissional (auto-criado)
├── requirements.txt          # Dependências do projeto
└── README.md                # Este arquivo
```

## Sistema de Armazenamento

O sistema utiliza arquivos JSON para persistência de dados:

- **recibos_saude.json**: Armazena todos os recibos de saúde salvos
- **<apelido>_despesas_profissionais.json**: Armazena as despesas profissionais do usuário logado

Os dados são salvos automaticamente quando você clica em "Salvar" e podem ser:
- **Editados**: Clique em "Editar" para carregar no formulário
- **Deletados**: Clique em "Deletar" com confirmação
- **Exportados**: Clique em "Exportar para CSV" para gerar arquivo compatível com a Receita Federal

## Design Responsivo

A aplicação se adapta automaticamente ao tamanho da sua tela:
- **Largura**: Utiliza 90% da largura da tela
- **Altura**: Utiliza 85% da altura da tela
- **Posicionamento**: Centraliza na tela automaticamente
- **Scroll Automático**: Formulários e listas possuem scrollbars dinâmicas quando o conteúdo excede o espaço disponível
- **Redimensionamento**: A interface reajusta ao redimensionar a janela

Funciona perfeitamente em:
- Telas pequenas (1024x768)
- Telas médias (1920x1080)
- Telas grandes (2560x1440 e superiores)

## Formatos de Arquivo CSV

### Receita Saúde - Padrão Receita Federal

Formato: Semocolon-delimited sem cabeçalho, 16 colunas

```
Data;Código;Inscrição;Valor;;Descrição;Tipo;CPF_Pagador;CPF_Prof;;;;S;CPF_Prof;REGISTRO_PROFISSIONAL
```

**Campos:**
1. Data (dd/mm/aaaa)
2. Código de Receita (ex: R01.001.001)
3. Número de Inscrição (ex: 06/23007)
4. Valor em R$ (ex: 999999,99)
5. Vazio
6. Descrição/Observações
7. Tipo de Pagador (PF ou EX)
8. CNPJ/CPF do Pagador (somente números)
9. CNPJ/CPF do Dependente (somente números)
10. Vazio
11. Vazio
12. Vazio
13. Vazio
14. S (sempre S)
15. CPF Profissional
16. REGISTRO_PROFISSIONAL

### Despesas Profissionais - Padrão Receita Federal

Formato padrão: Semicolon-delimited sem cabeçalho.

**Regra Especial:**
- **Apenas o código `P10.01.00006`** (Pagamento de Emolumentos pagos a terceiros) pode incluir os campos `competencia`, `multa` e `juros`
- Todos os outros códigos exportam apenas os **4 campos básicos**

Para o código `P10.01.00006`:

```
Data;Código;Valor;Descrição;Multa;Juros;Competência
```

Para todos os outros códigos (incluindo `P11.01.00006`):

```
Data;Código;Valor;Descrição
```

**Campos padrão:**
1. Data (dd/mm/aaaa)
2. Código de Despesa (ex: P20.01.00001)
3. Valor em R$ (ex: 999999,99)
4. Descrição da Despesa
5. Multa (apenas para `P10.01.00006`)
6. Juros (apenas para `P10.01.00006`)
7. Competência (mm/aaaa - apenas para `P10.01.00006`)

**Códigos de Despesa Válidos:**
- P20.01.00001 - Previdência Oficial
- P20.01.00002 - Pensão Alimentícia
- P20.01.00003 - Imposto Pago no Exterior
- P20.01.00004 - Imposto Pago
- P20.01.00005 - Outras Despesas

### Validação de Dados

Os arquivos gerados são automaticamente validados para:
- Formato de data correto (dd/mm/aaaa)
- Valores numéricos com vírgula decimal
- Campos obrigatórios preenchidos
- Códigos válidos conforme padrão Receita Federal

## Formatos de Dados Antigos

### Receita Saúde

**Campos Fixos (não editáveis):**
- **Código de Receita**: R01.001.001
- **Número de Inscrição**: 255
- **Tipo de Pagador**: PF
- **Tipo de Registro**: 06/23007

**Campos Editáveis no Formulário:**
- **Data de Pagto** (dd/mm/aaaa) - obrigatório - Clique no botão 📅 para selecionar via calendário
- **Valor** (R$) - obrigatório - Formato: 999999999,99
- **Descrição/Observações (Sessões)** - Gerada automaticamente via seletor de múltiplas datas:
  - Clique no botão 📆 para abrir o calendário
  - Selecione os dias das sessões (ficam destacados em cinza)
  - O sistema gera automaticamente:
    - 1 sessão: "Referente a 01 sessão de psicoterapia realizada no dia dd/mm/aaaa."
    - 3 sessões: "Referente a 03 sessões de psicoterapia realizadas nos dias data1, data2 e data3."
    - 12 sessões: "Referente a 12 sessões de psicoterapia realizadas nos dias data1, data2, ... e data12."
  - Clique em OK para confirmar ou Cancelar para fechar
  - Número de sessões sempre em formato 2 dígitos (01, 02... 12+)
- **CNPJ/CPF Pagador** - Número sem formatação (opcional)
- **CPF do Beneficiário** - CNPJ/CPF Profissional (opcional) - Valor padrão: 08750012894

### Despesas

**Campos Editáveis no Formulário:**
- **Data de Pagto** (dd/mm/aaaa) - obrigatório - Clique no botão 📅 para selecionar via calendário
- **Código de Despesa** - Exemplo: P20.01.00001 (obrigatório)
- **Valor** (R$) - obrigatório - Formato: 999999999,99
- **Descrição** - Texto descritivo da despesa (obrigatório)
- **Valor Complementar** - Campo adicional (opcional)
- **Competência** (mm/aaaa) - opcional

## Códigos de Despesa Disponíveis

| Código | Descrição |
|--------|-----------|
| P20.01.00001 | Previdência Oficial |
| P20.01.00002 | Pensão Alimentícia |
| P20.01.00003 | Imposto Pago no Exterior |
| P20.01.00004 | Imposto Pago |
| P20.01.00005 | Outras Despesas |

## Validações e Comportamento

### Receita Saúde
- ✓ Data de Pagto com seletor visual de calendário (navegue por mês/ano)
- ✓ Data deve estar no formato dd/mm/aaaa
- ✓ Valor deve ser um número válido com ponto ou vírgula como separador
- ✓ Campos fixos são desabilitados e pré-preenchidos
- ✓ Ao adicionar, o formulário limpa apenas os campos editáveis
- ✓ Exibe lista de receitas adicionadas antes de exportar

### Despesas
- ✓ Data de Pagto com seletor visual de calendário (navegue por mês/ano)
- ✓ Data deve estar no formato dd/mm/aaaa
- ✓ Valor deve ser um número válido
- ✓ Campos obrigatórios são validados antes de adicionar
- ✓ Exibe lista de despesas adicionadas antes de exportar

## Seletores de Data (Calendar Pickers)

### Seletor de Data Única (Data de Pagto)

O campo de data em ambos os formulários inclui um seletor de calendário visual:

- **Botão 📅**: Clique para abrir o calendário
- **Navegação**: Use os botões ◀ e ▶ para navegar entre meses
- **Seleção**: Clique em um dia para selecioná-lo
- **Confirmação**: Clique em OK para confirmar ou Cancelar para fechar

As datas podem ser inseridas manualmente (dd/mm/aaaa) ou selecionadas via calendário.

### Seletor de Múltiplas Datas (Descrição/Observações de Sessões)

O campo de descrição agora possui um seletor avançado de múltiplas datas para registrar sessões:

- **Botão 📆**: Clique para abrir o calendário de múltiplas seleções
- **Navegação**: Use os botões ◀ e ▶ para navegar entre meses
- **Seleção de Datas**: 
  - Clique em um dia para selecioná-lo (fica destacado em cinza #4a4a4a)
  - Clique novamente para desselecionar
  - Selecione quantos dias desejar (sem limite)
- **Visualização**: "Datas selecionadas: X" mostra quantas datas foram marcadas
- **Ordenação**: As datas são automaticamente ordenadas em ordem crescente
- **Limpeza**: Clique em "Limpar Seleção" para resetar todas as datas
- **Geração Automática**: 
  - Ao confirmar (OK), o sistema gera automaticamente a descrição
  - Formata com número de sessões em 2 dígitos (01, 02... 12, 13+)
  - Diferencia singular/plural corretamente:
    - **1 sessão**: "Referente a 01 sessão de psicoterapia realizada no dia 20/01/2026."
    - **2+ sessões**: "Referente a 03 sessões de psicoterapia realizadas nos dias 20/01/2026, 21/01/2026 e 22/01/2026."
  - Usa vírgula e espaço entre as datas, e "e" antes da última data
- **Confirmação**: Clique em OK para aplicar ou Cancelar para descartar

## Geração de Arquivos CSV

### Nomes de Arquivo
- **Receita Saúde**: `receita_saude_DDMMAAAA.csv`
- **Despesas**: `despesas_medicas_DDMMAAAA.csv`

### Formato de Exportação
- Delimitador: ponto-e-vírgula (;)
- Encoding: UTF-8
- Compatível com Carnê Leão Web da Receita Federal

## Notas Importantes

- Os arquivos gerados devem ser compatíveis com a importação do Carnê Leão Web
- Os campos fixos são automaticamente incluídos ao exportar
- Verifique o documento "Instruções para Utilização dos Arquivos de Modelos" para detalhes adicionais
- Sempre faça backup dos seus dados antes de importar na Receita Federal
- Use valores com ponto ou vírgula decimal (ex: 1000,50 ou 1000.50)

## Troubleshooting

**Erro: "Data deve estar no formato dd/mm/aaaa"**
- Verifique se a data está no formato correto (ex: 15/01/2026)

**Erro: "Valor deve ser um número válido"**
- Use apenas números e separador decimal (ponto ou vírgula)
- Exemplo: 1500,00 ou 1500.00

**Erro de Validação de CPF**
- Verifique se o CPF digitado é válido (dígitos verificadores)
- O sistema destaca o campo em vermelho se inválido
- Selecione preferencialmente da lista suspensa para evitar erros

**Arquivo não foi criado**
- Verifique se você tem permissão de escrita na pasta selecionada
- Verifique se há espaço em disco disponível

## Suporte

Para dúvidas sobre os formatos de dados ou campos específicos, consulte o documento de instruções fornecido pela Receita Federal: "Instruções para Utilização dos Arquivos de Modelos para Importação da Escrituração no Carnê Leão Web".
