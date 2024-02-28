from conversor_pdf_para_texto import extrair_texto_pdf
import json

senha = '16164177731'
path = './Fatura_012024_GUILHERME_7437_MASTER_00151185012140.PDF'

infos = path.split('_')
mes = infos[1][:2] 
ano = infos[1][2:]
nome = infos[2]
ult_digitos = infos[3]

fatura_texto = extrair_texto_pdf(path, senha)

linhas_da_fatura = fatura_texto.split("\n")


dados = []
gastos_unitarios = []


def obter_detalhamento_fatura(linhas):
    detalhamento_fatura = [] 
    ler_linha = False

    for linha in linhas:
        if "Detalhamento da Fatura" in linha:
            ler_linha = True
            continue
        
        if "Resumo da Fatura" in linha:
            ler_linha = False

        if ler_linha:
            detalhamento_fatura.append(linha)
    
    linhas_corrigidas = corrigir_quebra_de_linha(detalhamento_fatura)
    return linhas_corrigidas

def corrigir_quebra_de_linha(linhas):
    for index, linha in enumerate(linhas):
        if linha.strip()[0].isdigit() and not linha.strip()[-1].isdigit():
            palavra = ''
            for carac in linha[-1::-1]:  
                if not carac.isdigit():
                    palavra = carac + palavra
                else: 
                    break
  
            linha = linha[:-len(palavra)]  

            linhas[index] = linha   
            linhas.pop(index+1) 
    
    return linhas


def separar_fatura_por_cartoes(fatura, nome_titular):
    detalhamento_fatura = obter_detalhamento_fatura(fatura)
    fatura_separada_em_cartoes = []

    for linha in detalhamento_fatura:
        if nome_titular in linha:
            fatura_separada_em_cartoes.append([])

        fatura_separada_em_cartoes[-1].append(linha)

    return fatura_separada_em_cartoes


def obter_tipo_e_data(infos_lancamento):
    if infos_lancamento[0].isdigit():
        tipo = infos_lancamento[0]
        data = infos_lancamento[1] + "/" + ano
    else:
        tipo = ""
        data = infos_lancamento[0] + "/" + ano

    return tipo, data


def obter_estabelecimento(infos_lancamento):
    inicio_estab = 0
    fim_stab = len(infos_lancamento)
    inicio_estab_found = False

    for index, info in enumerate(infos_lancamento):
        if info[0].isdigit() and info[-1].isdigit() and "/" in info and not inicio_estab_found:
            inicio_estab = index + 1
            inicio_estab_found = True
        elif (info[0].isdigit() or (info[0] == "-" and info[1].isdigit())) and info[-1].isdigit() and ("/" in info or "," in info):
            fim_stab = index
            break

    estabelecimento = ''
    for info in infos_lancamento[inicio_estab:fim_stab]:
        if estabelecimento == "":
            estabelecimento = estabelecimento + info
        else:
            estabelecimento = estabelecimento + " " + info

    return estabelecimento, fim_stab


def obter_parcelas_e_precos_lancamento(infos_lancamento, indice_fim_estabelecimento):
    count_prices = 0
    parcelas = '' 
    valorBRL = '' 
    valorUSD = ''

    # TODO: melhorar lógica para caso de haver dolar (se houver dolar, pode ser que nao haja informação de gasto em real e a lógica abaixo fica comprometida)

    for info in infos_lancamento[indice_fim_estabelecimento:]:
        if "/" in info:
            parcelas = info
        elif "," in info:
            if count_prices == 0:
                valorBRL = float(info.replace(".","").replace(",","."))
                valorUSD = 0.00
            else:
                valorUSD = float(info.replace(".","").replace(",","."))
            count_prices += 1
    
    return parcelas, valorBRL, valorUSD


def tirar_strings_vazias_de_lista(lista_strings):
    infos_sem_espaco = filter(lambda x: x != '', lista_strings)
    infos_sem_espaco = list(infos_sem_espaco)

    return infos_sem_espaco


def criar_lancamentos(linha_lancamento):
    infos_linha = linha_lancamento.strip().split(" ")
    infos_sem_espaco = tirar_strings_vazias_de_lista(infos_linha)

    tipo, data = obter_tipo_e_data(infos_sem_espaco)
    estabelecimento, fim_stab = obter_estabelecimento(infos_sem_espaco)
    parcelas, valorBRL, valorUSD = obter_parcelas_e_precos_lancamento(infos_sem_espaco, fim_stab)

    lancamento = {
        'tipo': tipo,
        'data': data,
        'estabelecimento': estabelecimento,
        'parcelas': parcelas,
        'valorBRL': valorBRL,
        'valorUSD': valorUSD,
    }

    return lancamento
 
            
def obter_final_cartao_por_linha(primeira_linha): 
    final_cartao = primeira_linha[-4:]

    return final_cartao


def criar_cartao(linhas_cartao):
    final_cartao = ''
    totalBRL = '' 
    totalUSD = ''
    tipos_lancamento = []

    linhas_cartao_limpas = tirar_strings_vazias_de_lista(linhas_cartao)

    for index, linha in enumerate(linhas_cartao_limpas): 
        if index == 0:
            final_cartao = obter_final_cartao_por_linha(linha)
        elif "VALOR TOTAL" in linha:  
            totalBRL = linha.strip().split(" ")[-2]
            totalBRL_to_float = float(totalBRL.replace(".","").replace(",","."))

            totalUSD = linha.strip().split(" ")[-1]
            totalUSD_to_float = float(totalUSD.replace(".","").replace(",","."))
        elif "Compra Data Descrição Parcela R$ US$" in linha:
            tipos_lancamento.append({
                'tipo': linhas_cartao[index-1], 
                'lancamentos': []
            })
        elif linha.strip()[0].isdigit() and linha.strip()[-1].isdigit():
            lancamento = criar_lancamentos(linha)
            tipos_lancamento[-1]['lancamentos'].append(lancamento)

    cartao = {
        'final_cartao': final_cartao,
        'totalBRL': totalBRL_to_float,
        'totalUSD': totalUSD_to_float,
        'tipos_lancamento': tipos_lancamento
    }

    return cartao


cartoes_separados_em_linhas = separar_fatura_por_cartoes(linhas_da_fatura, nome)


for cartao_linhas in cartoes_separados_em_linhas:
    cartao = criar_cartao(cartao_linhas)
    dados.append(cartao)



json_formatado = json.dumps(dados, indent=2)

with open(f"{path[2:-4]}.json", "w", encoding='utf-8') as outfile: 
    outfile.write(json_formatado)




