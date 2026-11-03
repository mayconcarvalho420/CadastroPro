
import re


def normalizar_cpf(cpf):
    if not isinstance(cpf, str):
        raise ValueError('O CPF deve ser uma string.')

    cpf = cpf.strip()

    # Aceita 11 dígitos ou o formato XXX.XXX.XXX-XX
    formato_valido = (
        re.fullmatch(r'[0-9]{11}', cpf)
        or re.fullmatch(r'[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}', cpf)
    )

    if not formato_valido:
        raise ValueError('Formato de CPF inválido.')

    return re.sub(r'[^0-9]', '', cpf)


def validar_cpf(cpf):
    try:
        cpf = normalizar_cpf(cpf)
    except ValueError:
        return False

    # Impede sequências repetidas
    if cpf == cpf[0] * 11:
        return False

    # Primeiro dígito verificador
    nove_dig = cpf[:9]
    contador_reg_1 = 10
    resultado_digito_1 = 0

    for digito in nove_dig:
        resultado_digito_1 += int(digito) * contador_reg_1
        contador_reg_1 -= 1

    digito_1 = (resultado_digito_1 * 10) % 11
    digito_1 = digito_1 if digito_1 <= 9 else 0

    # Segundo dígito verificador
    dez_dig = nove_dig + str(digito_1)
    contador_reg_2 = 11
    resultado_digito_2 = 0

    for digito in dez_dig:
        resultado_digito_2 += int(digito) * contador_reg_2
        contador_reg_2 -= 1

    digito_2 = (resultado_digito_2 * 10) % 11
    digito_2 = digito_2 if digito_2 <= 9 else 0

    cpf_calculado = f'{nove_dig}{digito_1}{digito_2}'

    return cpf == cpf_calculado
