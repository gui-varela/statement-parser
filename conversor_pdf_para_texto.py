import PyPDF2
# def extrair_texto_pdf(nome_arquivo_pdf, nome_arquivo_texto, senha):
def extrair_texto_pdf(nome_arquivo_pdf, senha):
    fatura = ""
    with open(nome_arquivo_pdf, 'rb') as arquivo_pdf:
        leitor = PyPDF2.PdfReader(arquivo_pdf)

        # Verifica se o arquivo PDF está protegido por senha
        if leitor.is_encrypted:
            # Tenta desbloquear o arquivo com a senha fornecida
            try:
                leitor.decrypt(senha)
            except PyPDF2.PdfReadError:
                print("A senha fornecida é incorreta. Não é possível desbloquear o arquivo.")
                return

        numero_paginas = len(leitor.pages)

        for pagina_numero in range(numero_paginas):
                pagina = leitor.pages[pagina_numero]
                texto = pagina.extract_text()
                fatura =  fatura + texto

        """ with open(nome_arquivo_texto, 'w', encoding='utf-8') as arquivo_texto:
            for pagina_numero in range(numero_paginas):
                pagina = leitor.pages[pagina_numero]
                texto = pagina.extract_text()
                arquivo_texto.write(texto + '\n')
                fatura =  fatura + texto  """

    # print(f"As informações do arquivo PDF foram extraídas para '{nome_arquivo_texto}'.")
    return fatura

# Substitua 'arquivo_protegido.pdf' pelo nome do arquivo PDF protegido
# Substitua 'saida.txt' pelo nome do arquivo de texto de saída que você deseja criar
senha_do_pdf = '16164177731'  # Coloque a senha do seu arquivo PDF aqui


