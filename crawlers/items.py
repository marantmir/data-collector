import scrapy


class CompanyItem(scrapy.Item):
    cnpj = scrapy.Field()
    razao_social = scrapy.Field()
    nome_fantasia = scrapy.Field()
    cnae_principal = scrapy.Field()
    cnae_secundarias = scrapy.Field()
    natureza_juridica = scrapy.Field()
    porte = scrapy.Field()
    situacao_cadastral = scrapy.Field()
    data_situacao = scrapy.Field()
    regime_tributario = scrapy.Field()
    capital_social = scrapy.Field()
    endereco = scrapy.Field()
    contato = scrapy.Field()
    source_id = scrapy.Field()


class PartnerItem(scrapy.Item):
    company_cnpj = scrapy.Field()
    cpf_cnpj = scrapy.Field()
    nome = scrapy.Field()
    qualificacao = scrapy.Field()
    percentual = scrapy.Field()
    data_entrada = scrapy.Field()
    source_id = scrapy.Field()


class FinancialItem(scrapy.Item):
    company_cnpj = scrapy.Field()
    tipo = scrapy.Field()
    ano_exercicio = scrapy.Field()
    trimestre = scrapy.Field()
    data_referencia = scrapy.Field()
    valores = scrapy.Field()
    moeda = scrapy.Field()
    audited = scrapy.Field()
    source_url = scrapy.Field()
    source_id = scrapy.Field()


class BidItem(scrapy.Item):
    orgao_responsavel = scrapy.Field()
    modalidade = scrapy.Field()
    numero_licitacao = scrapy.Field()
    objeto = scrapy.Field()
    valor_estimado = scrapy.Field()
    data_abertura = scrapy.Field()
    data_resultado = scrapy.Field()
    situacao = scrapy.Field()
    company_cnpj = scrapy.Field()
    valor_contratado = scrapy.Field()
    source_url = scrapy.Field()
    source_id = scrapy.Field()
