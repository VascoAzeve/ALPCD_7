import typer
import requests
import csv
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

# Função para buscar as principais habilidades
def get_top_skills(job_url):
    try:
        response = requests.get(job_url, headers=headers_scrap)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        job_cards = soup.find_all("div", class_="jobInfoCard")
        skill_counts = {}

        for card in job_cards:
            details_link = card.find("a", class_="title noclick")
            if details_link:
                job_details_url = "https://www.ambitionbox.com" + details_link["href"]

                try:
                    details_response = requests.get(job_details_url, headers=headers_scrap)
                    details_response.raise_for_status()

                    details_soup = BeautifulSoup(details_response.content, "html.parser")
                    skills_section = details_soup.find("div", class_="jd-insights")

                    if skills_section:
                        skills = skills_section.find_all("a", class_="chip")
                        for skill in skills:
                            skill_name = skill.text.strip()
                            skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
                except requests.exceptions.RequestException as e:
                    typer.echo(f"Erro ao buscar detalhes do trabalho em {job_details_url}: {e}")
                    continue

        # Ordenar habilidades por frequência e retornar as 10 principais
        top_skills = dict(sorted(skill_counts.items(), key=lambda item: item[1], reverse=True)[:10])
        return top_skills

    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro ao buscar listagens de trabalho: {e}")
        return {}

# Comando para buscar as principais habilidades de um título de trabalho
@app.command()
def skills(job_title: str):
    """Busca as principais habilidades para um cargo."""
    job_url = f"https://www.ambitionbox.com/jobs/search?tag={job_title.replace(' ', '%20')}"
    typer.echo(f"Buscando habilidades para: {job_title}")

    top_skills = get_top_skills(job_url)

    if top_skills:
        typer.echo(f"Top 10 habilidades para {job_title}:")
        for skill, count in top_skills.items():
            typer.echo(f"- {skill}: {count} ocorrências")
    else:
        typer.echo("Não foi possível recuperar as habilidades.")

# Outras funções e comandos existentes...

if __name__ == "__main__":
    app()
