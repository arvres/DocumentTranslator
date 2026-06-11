# 📄 Document Translator

Um tradutor de documentos baseado em OCR (Reconhecimento Óptico de Caracteres) e Inteligência Artificial, capaz de extrair texto de imagens, traduzir automaticamente para português e gerar um PDF pesquisável com o conteúdo traduzido.

## 🎯 Objetivo

O projeto foi desenvolvido para automatizar a tradução de documentos digitalizados, imagens escaneadas, currículos, artigos e outros conteúdos textuais presentes em imagens.

Ao invés de apenas sobrepor texto traduzido sobre a imagem original, o sistema reconstrói o documento em formato PDF, tornando-o mais limpo, legível e pesquisável.

---

## 🚀 Funcionalidades

* Extração de texto utilizando OCR
* Detecção automática de orientação do documento
* Tradução automática para português
* Agrupamento inteligente de linhas em parágrafos
* Geração de PDF pesquisável
* Sistema de cache para otimizar traduções repetidas
* Estrutura modular e escalável

---

## 🧠 Como funciona

O sistema segue o seguinte fluxo:

```text
Imagem
   ↓
PaddleOCR
   ↓
Extração dos blocos de texto
   ↓
Agrupamento de parágrafos
   ↓
Tradução automática
   ↓
Reconstrução do documento
   ↓
PDF em português
```

---

## 🛠 Tecnologias Utilizadas

### OCR

* PaddleOCR 2.8.1
* PaddlePaddle 2.6.2

### Processamento de Imagem

* OpenCV
* NumPy

### Tradução

* Deep Translator
* Google Translate

### Geração de PDF

* ReportLab

---

## 📂 Estrutura do Projeto

```text
Smart-Document-Translator/
│
├── imgs/
│
├── output/
│
├── app.py
│
├── requirements.txt
│
└── README.md
```

---

## ⚙️ Requisitos

* Python 3.11

> ⚠️ O projeto foi desenvolvido e testado utilizando Python 3.11. Versões mais recentes podem apresentar incompatibilidades com o PaddleOCR.

---

## 📦 Instalação

Clone o repositório:

```bash
git clone https://github.com/arvres/DocumentTranslator
```

Acesse a pasta do projeto:

```bash
cd DocumentTranslator
```

Crie um ambiente virtual:

```bash
py -3.11 -m venv venv
```

Ative o ambiente virtual:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## ▶️ Execução

Adicione a imagem que deseja traduzir dentro da pasta:

```text
imgs/
```

Altere o caminho da imagem no arquivo:

```python
IMAGEM = "imgs/SUA-IMAGEM"
```

Execute:

```bash
python app.py
```

Ao final do processamento, o PDF traduzido será gerado em:

```text
output/documento_traduzido.pdf
```

---

## 📈 Exemplo de Aplicação

O projeto pode ser utilizado para:

* Currículos internacionais
* Artigos acadêmicos
* Documentos corporativos
* Relatórios financeiros
* Materiais educacionais
* Documentos digitalizados

---

## 🔍 Diferenciais do Projeto

Diferentemente de tradutores convencionais baseados apenas em OCR, este projeto:

* Reconstrói o documento em PDF
* Agrupa automaticamente linhas relacionadas
* Melhora a qualidade da tradução através do contexto
* Gera um documento pesquisável
* Possui arquitetura modular para futuras melhorias

---

## 🔮 Melhorias Futuras

* Preservação completa do layout original
* Suporte a múltiplos idiomas de saída
* Interface gráfica
* Processamento de PDFs multipágina
* Integração com IA para correção contextual
* Detecção automática de títulos, tabelas e listas

---

## 👨‍💻 Autor

Pedro Alves

Projeto desenvolvido para fins acadêmicos e estudo de OCR, processamento de imagens e tradução automática utilizando Inteligência Artificial.

```
```
