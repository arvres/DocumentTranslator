
import os
import cv2

# Biblioteca responsável pelo OCR
from paddleocr import PaddleOCR

# Biblioteca utilizada para tradução automática
from deep_translator import GoogleTranslator

# Bibliotecas para criação do PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import enums

# ==================================================
# CONFIGURAÇÕES DO PROJETO
# ==================================================

# Imagem que será processada
IMAGEM = "imgs/doc2.jpg"

# Caminho do PDF final
PDF_SAIDA = "output/documento_traduzido.pdf"

# Cria a pasta de saída caso ela não exista
os.makedirs("output", exist_ok=True)

# ==================================================
# INICIALIZAÇÃO DO OCR
# ==================================================

print("==================================================")
print("----------- Inicializando PaddleOCR... ---------")
print("==================================================")


# cria o modelo OCR
ocr = PaddleOCR(
    use_angle_cls=True, # corrige textos inclinados ou rotacionados
    lang="en" # otimizado para documentos em inglês
)

# Carrega a imagem
imagem = cv2.imread(IMAGEM)

# Verificação de segurança
if imagem is None:
    raise Exception("Não foi possível abrir a imagem.")

# ==================================================
# EXECUÇÃO DO OCR
# ==================================================

# O PaddleOCR retorna:

# - Bounding Box (posição do texto)
# - Texto reconhecido
# - Confiança da leitura

resultado = ocr.ocr(imagem, cls=True)

# ==================================================
# EXTRAÇÃO DOS BLOCOS DE TEXTO
# ==================================================

print("==================================================")
print("-------------- Extraindo blocos... --------------")
print("==================================================")

blocos = []

for item in resultado[0]:

    # Coordenadas do bloco
    bbox = item[0]

    # Texto reconhecido
    texto = item[1][0]

    # Coordenada superior do bloco utilizada para ordenar o documento
    y_top = min(p[1] for p in bbox)

    blocos.append({"texto": texto, "y": y_top})

# ==================================================
# ORDENAÇÃO DOS BLOCOS
# ==================================================

# Organiza todos os textos de cima para baixo para reconstruir a ordem correta do documento

blocos.sort(key=lambda x: x["y"])

# ==================================================
# AGRUPAMENTO DE PARÁGRAFOS
# ==================================================
print("==================================================")
print("------------ Agrupando parágrafos... ------------")
print("==================================================")

paragrafos = []

paragrafo_atual = ""

ultimo_y = None

# Distância máxima (em pixels) para considerar que duas linhas pertencem ao mesmo parágrafo
DISTANCIA_MAXIMA = 18

for bloco in blocos:

    texto = bloco["texto"]
    y = bloco["y"]

    # Primeiro bloco encontrado

    if ultimo_y is None:

        paragrafo_atual = texto

    # Se as linhas estiverem próximas elas serão unidas em um mesmo parágrafo

    elif abs(y - ultimo_y) <= DISTANCIA_MAXIMA:

        paragrafo_atual += " " + texto

    # Caso contrário inicia um novo parágrafo

    else:

        paragrafos.append(paragrafo_atual)

        paragrafo_atual = texto

    ultimo_y = y

# Adiciona o último parágrafo

if paragrafo_atual:
    paragrafos.append(paragrafo_atual)

print("==================================================")
print(f"--------- {len(paragrafos)} parágrafos encontrados. ---------")
print("==================================================")

# ==================================================
# TRADUÇÃO
# ==================================================

print("==================================================")
print("------------- Traduzindo conteúdo... -----------")
print("==================================================")

# Cache para evitar traduzir o mesmo texto várias vezes
cache = {}

paragrafos_traduzidos = []

for texto in paragrafos:

    texto = texto.strip()

    # Ignora textos muito pequenos

    if len(texto) < 2:
        continue

    # Verifica se já foi traduzido

    if texto in cache:

        traducao = cache[texto]

    else:

        try:

            traducao = GoogleTranslator(source="auto", target="pt").translate(texto)

        except Exception:

            # Caso a tradução falhe
            # mantém o texto original

            traducao = texto

        cache[texto] = traducao

    paragrafos_traduzidos.append(traducao)

    print("OK ->", traducao[:60])

# ==================================================
# CRIAÇÃO DO PDF
# ==================================================

print("==================================================")
print("----------------- Gerando PDF... -----------------")
print("==================================================")

# Cria documento PDF
doc = SimpleDocTemplate(PDF_SAIDA)

# Estilos prontos do ReportLab
styles = getSampleStyleSheet()

# Estilo para títulos
titulo_style = styles["Heading2"]
titulo_style.alignment = enums.TA_CENTER

# Estilo para parágrafos
texto_style = styles["BodyText"]

# Espaçamento entre linhas
texto_style.leading = 18

conteudo = []

# ==================================================
# RECONSTRUÇÃO DO DOCUMENTO
# ==================================================

for texto in paragrafos_traduzidos:

    texto_limpo = texto.strip()

    # Regra simples:
    # Se o texto for curto e estiver totalmente em maiúsculo, assume que é um título

    if (len(texto_limpo) < 40 and texto_limpo.upper() == texto_limpo):
        conteudo.append(Paragraph(texto_limpo, titulo_style))
    else:
        conteudo.append(Paragraph(texto_limpo, texto_style))

    # Espaço entre blocos
    conteudo.append(Spacer(1, 10))

# ==================================================
# GERAÇÃO FINAL DO PDF
# ==================================================

doc.build(conteudo)
print("==================================================")
print("------------ PDF criado com sucesso! -------------")
print("==================================================")


