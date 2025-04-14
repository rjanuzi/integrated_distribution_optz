# Gerador de Samples

## Requisitos

- Python 3.13.1
- Pandas 2.2.3
- Openpyxl 3.1.5

## Instruções

### Instalação de Dependências

```[bash]
python -m venv venv
source venv\Scripts\activate
pip install -r requirements.txt
```

Caso dê algum conflito entre a sua versão do Python e as versões das depedências, tente instala-las sem especificar uma versão, o uso deles nesse script é simples e não deve apresentar muitas complicações em versões diferentes.

### Execução

Basta executar o arquivo generate_sample.py

```[bash]
python generate_sample.py
```

Será criada uma pasta chamada "samples", dentro dela, os arquivos de sample serão gerados, sempre com o nome "YYYYmmdd_HHMMSS_sample.xlsx".

Os dados são gerados de forma randômica e com uma consistência básica entre nomes de campos (exemplo: nomes de linhas entre dados).

No inicio do arquivo existem algumas constates que podem ser utilizadas para manipular alguns aspectos dos dados gerados, como por exemplo:


- __DEFAULT_PERIODS: Para definir quantos dias de períodos considerar
- __DEFAULT_PLANTS: Número de plantas produtivas para considerar