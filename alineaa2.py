import typer
import requests
import json
from bs4 import BeautifulSoup

app = typer.Typer()
api_key = "422295b885ee1bc7fa94f330fbe85de2"

headers_api = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

headers_scrap = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

# 2 a) infos site
def get_company_info(company_name: str):
    search_url = f"https://www.ambitionbox.com/overview/{company_name.replace(' ', '-')}-overview"

    try:
        response = requests.get(search_url, headers=headers_scrap)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro ao buscar informações no AmbitionBox: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        # estrelas e avaliações
        rating = soup.find("span", class_="css-1jxf684 text-primary-text font-pn-700 text-xl !text-base").text.strip()
    except AttributeError:
        rating = None
        typer.echo("Estrelas e avaliações não encontradas.")

    try:
        # benefícios
        benefits_tag = soup.find("div", class_="css-175oi2r flex gap-1 pt-1 pb-5 md:py-4 px-3 items-start")
        benefits = [benefit_div.text.strip() for benefit_div in benefits_tag.find_all("div", recursive=False)] if benefits_tag else None
    except AttributeError:
        benefits = None
        typer.echo("Benefícios não encontrados.")

    try:
        # descrição da empresa
        description_tag = soup.find("div", class_="css-175oi2r p-0 md:p-5 gap-x-5 gap-y-8 md:flex-row md:flex-wrap md:justify-start flex-1 [&>*:nth-child(1)]:rounded-tr-md [&>*:nth-child(1)]:rounded-tl-md md:[&>*:nth-child(1)]:rounded-tr-none [&>*:nth-child(2)]:rounded-tr-md [&>*:nth-last-child(1)]:rounded-br-md md:[&>*:nth-last-child(2)]:rounded-bl-md pb-0 md:pb-5")
        description = " ".join([desc.text.strip() for desc in description_tag.find_all("div")]) if description_tag else None
    except AttributeError:
        description = None
        typer.echo("Descrição da empresa não encontrada.")

    return {
        "rating": rating,
        "evaluations": benefits,
        "description": description,
    }

# 2 a) comando juntar info site e api
@app.command() # id: 494385
def get(id:int):
    url = "https://api.itjobs.pt/job/get.json"
    # Monta os parâmetros da requisição
    params = {
        "api_key": api_key,
        "id": id,
    }
    try:
        response = requests.get(url, params=params, headers=headers_api)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro na requisição: {e}")
        raise typer.Exit(code=1)
    
    try:
        data = response.json()
    except ValueError:
        typer.echo("Erro: Resposta não está em formato JSON.")
        raise typer.Exit(code=1)
    
    # Buscar informações adicionais da empresa
    company_name = data.get("company", {}).get("name", "")
    if company_name:
        company_info = get_company_info(company_name)
        if company_info:
            data.update(company_info)
            typer.echo(data)


if __name__ == "__main__":
    app()
