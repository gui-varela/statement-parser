from conversor_pdf_para_texto import extrair_texto_pdf
import json

senha = '12216'
path = './Fatura XP - dezembro 2023.pdf'

fatura_texto = extrair_texto_pdf(path, senha)

linhas = fatura_texto.split("\n")

gastos = []

ler_linha = False

for linha in linhas:
    if "Subtotal " in linha:
        ler_linha = False

    if ler_linha:
        gastos.append(linha)

    if "Data Descrição R$ US$" in linha:
        ler_linha = True
    

lancamentos = [] 


for gasto in gastos:
    if "Pagamentos Validos Normais" in gasto:
        continue

    gasto_infos = gasto.split(" ")

    lancamento = {}
    estabelecimento = ''

    for info in gasto_infos[1:-2]:
        estabelecimento = estabelecimento + info + " "

    valor_em_real = float(gasto_infos[-2].replace(".","").replace(",","."))
    valor_em_dolar = float(gasto_infos[-1].replace(".","").replace(",","."))

    lancamento = {
        "data": gasto_infos[0],
        "estabelecimento": estabelecimento.strip(),
        "valor_real": valor_em_real,
        "valor_dolar": valor_em_dolar
    }

    lancamentos.append(lancamento)
 
json_formatado = json.dumps(lancamentos, indent=2)

with open(f"{path[2:-4]}.json", "w", encoding='utf-8') as outfile: 
    outfile.write(json_formatado)

