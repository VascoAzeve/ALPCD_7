import typer
import requests
import csv
import re
from datetime import datetime
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

# TP 1 -------------------------------------------------------------------------------------------------------------------------------
def imprimir_vagas_guardar_csv(data, nome_comando):
    vagas = []
    for job in data["results"]:
        publishedAt = job.get("publishedAt", "N/A")
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        description = " ".join(company.get("description", "N/A").splitlines()).strip()
        locations = job.get("locations", "N/A")
        if locations != "N/A":
            location_name = locations[0].get("name", "N/A")
        else:
            location_name = locations
        wage = job.get("wage", "N/A") or "N/A"

        typer.echo(f"Titulo: {title}")
        typer.echo(f"Empresa: {company['name']}")
        typer.echo(f"Localização: {location_name}")
        typer.echo(f"Descrição da empresa: {description}")
        typer.echo(f"Publicado em: {publishedAt}")
        typer.echo(f"Salário: {wage}")
        typer.echo("-" * 40)

        
        vagas.append({
            "titulo": title,
            "empresa": company["name"],
            "descricao": description,
            "data_publicacao": publishedAt,
            "salario": wage,
            "localizacao": location_name
        })

    guardar_csv = input("Deseja guardar as vagas em um arquivo CSV? (1 para guardar; 2 para não guardar)")
    while True: 
        if guardar_csv == "1":
            ficheiro = f"{nome_comando}.csv"
            with open(ficheiro, mode="a", newline='', encoding="utf-8") as csvfile:
                fieldnames = ["titulo", "empresa", "descricao", "data_publicacao", "salario", "localizacao"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(vagas)
            typer.echo(f"Vagas exportadas para o arquivo '{ficheiro}'.")
            break
        elif guardar_csv == "2": 
            break
        else: 
            guardar_csv = input("Opção inválida. Por favor, digite 1 para guardar e 2 para não guardar.")

#alinea a
@app.command()
def top(limite: int):
    url = "https://api.itjobs.pt/job/list.json"
    vagas = []
    if limite <= 0:
        typer.echo("O limite deve ser um número positivo.")
        raise typer.Exit(code=1)

    
    params = {
        "api_key": api_key,
        "limit": limite,
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

    if "results" not in data or not data["results"]:
        typer.echo("Nenhuma vaga encontrada.")
        return

    imprimir_vagas_guardar_csv(data, "job")

#alinea b
@app.command()
def search(localidade: str, empresa: str, numero_trabalhos: int):
    params = {
        "api_key": api_key,
        "q": empresa,
        "locations": localidade,
        "limit": numero_trabalhos,
        "full_time": "true"  #filtra apenas vagas full-time
    }

    url = "https://api.itjobs.pt/job/search.json"

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

    if "results" not in data or not data["results"]:
        typer.echo(f"Não foram encontradas vagas para a empresa {empresa} na localidade {localidade}.")
        raise typer.Exit(code=1)

    imprimir_vagas_guardar_csv(data, "search")

#alinea c
@app.command()
def salary(job_id: str):
    params = {
        "api_key": api_key,
        "id": job_id,
    }

    url = "https://api.itjobs.pt/job/get.json"

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
    

    wage = data.get("wage")
    if wage:
        typer.echo(wage)
    else:
        #tenta extrair salário usando expressões regulares em outros campos
        body = data.get("body", "")
        #procurar valores numéricos seguidos de "€" ou "euros"
        match = re.findall(r"(\d{1,3}(?:[.,]\d{3})*(?:-\d{1,3}(?:[.,]\d{3})*)?)\s?(€|euros?)", body, re.IGNORECASE)
        
        if match:
            #salario_extraido = match.group(1)
            typer.echo(match)
        else:
            typer.echo("Salário não especificado.")
            
#alinea d 
@app.command()
def skills(skills: list[str], data_inicial: str, data_final: str):
    url = "https://api.itjobs.pt/job/search.json"
    skill_query = ",".join(skills)
    data_inicial_dt = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final_dt = datetime.strptime(data_final, "%Y-%m-%d")

    page = 1
    encontrou_vaga = False
    vagas = []

    while True:
        params = {
            "api_key": api_key,
            "q": skill_query,
            "page": page,
            "limit": 999
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

        # Se não houver resultados, pare o loop
        if "results" not in data or not data["results"]:
            typer.echo("Estas são as vagas encontradas com as skills e datas informadas.")
            break

        # Processa cada resultado
        for job in data["results"]:
            published_at_str = job.get("publishedAt", "N/A")
            try:
                published_at_dt = datetime.strptime(published_at_str, "%Y-%m-%d %H:%M:%S")
                if data_inicial_dt <= published_at_dt <= data_final_dt:
                    encontrou_vaga = True
                    imprimir_vagas_guardar_csv(data, "skills")
            except ValueError:
                typer.echo(f"Data inválida ou em formato inesperado: {published_at_str}")
                continue
        page += 1
    if not encontrou_vaga:
        typer.echo("Nenhuma vaga encontrada com as skills e datas informadas.")

# TP2 ----------------------------------------------------------------------------------------------------------------------------


# Funções -----------------------------------------------------------
# 2 a) c) guardar csv
# Função para salvar dados em CSV corretamente
def save_to_csv(data, filename):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            if isinstance(data, dict):  
                writer = csv.writer(file)
                writer.writerow(["Chave", "Valor"])  
                for key, value in data.items():
                    writer.writerow([key, value])
            elif isinstance(data, list):  
                if data: 
                    fieldnames = data[0].keys()  
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()  
                    writer.writerows(data) 
            typer.echo(f"Dados salvos no arquivo: {filename}")
    except Exception as e:
        typer.echo(f"Erro ao salvar dados no arquivo CSV: {e}")

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

# 2 b)  estatisticas zona cargo nr
def save_statistics(data):
    stats = {}

    for job in data:
        zone = job.get("locations", [{"name": "Desconhecida"}])[0]["name"]
        job_type = job.get("title", "Desconhecido")

        if zone not in stats:
            stats[zone] = {}

        if job_type not in stats[zone]:
            stats[zone][job_type] = 0

        stats[zone][job_type] += 1

    return stats

# 2 b) guardar csv
def save_detailed_to_csv(stats, filename="job_statistics.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Cabeçalho com 3 colunas
        writer.writerow(["Zona", "Tipo de Trabalho", "Nº de vagas"])

        # Iterar pelos dados detalhados e escrever no CSV
        for zone, job_types in stats.items():
            for job_type, count in job_types.items():
                writer.writerow([zone, job_type, count])

    print(f"Ficheiro de exportação criado com sucesso: {filename}")

# 2 c) skills
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
        typer.echo(f"Erro ao buscar os trabalhos: {e}")
        return {}

# 2 d) indeed dados
def get_company_info_indeed(company_name: str):
    search_url = f"https://pt.indeed.com/cmp/{company_name.replace(' ', '-')}"

    try:
        response = requests.get(search_url, headers=headers_scrap)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro ao buscar informações no Indeed: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        # estrelas e avaliações
        rating = soup.find("span", class_="css-74t09c e1wnkr790").text
        evaluations = soup.find("a", class_="css-fo75d1 e19afand0")
        #  descrição da empresa
        description_local = soup.find("ul", class_="css-hbpv4x e37uo190")
        description = description_local.findAll("div").text


        return {
            "rating": rating,
            "evaluations": evaluations,
            "description": description,
        }
    except AttributeError:
        typer.echo("Informações da empresa não encontradas no Indeed.")
        return None

# Comandos --------------------------------------------------------

# 2 a) comando juntar info site e api
@app.command()  # id: 494385
def get(id: int):
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

    typer.echo(f"Informações do trabalho: {data}")
                
    save = typer.confirm("Deseja salvar as informações no arquivo CSV? (sim/nao)")
    if save:
        save_to_csv([data], f"job_{id}_details.csv")  # Passa como lista para garantir o formato adequado
    else:
        typer.echo("Informações não foram salvas.")
           

# 2 b) comando csv estatisticas
@app.command()
def statistics():
    print("A guardar dados de trabalho...")
    page = 1
    all_jobs = []

    while True:
        url = "https://api.itjobs.pt/job/search.json"
        params = {
            "api_key": api_key,
            "page": page,
        }

        try:
            response = requests.get(url, params=params, headers=headers_api)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            typer.echo(f"Erro na requisição: {e}")
            raise typer.Exit(code=1)

        data = response.json()

        # Verifique se 'results' está presente na resposta e se não está vazio
        if 'results' not in data or not data['results']:
            break

        all_jobs.extend(data['results'])
        page += 1

    
    print("Guardar estatísticas detalhadas...")
    stats = save_statistics(all_jobs)
    save_detailed_to_csv(stats)

    print("Ficheiro csv criado com sucesso!")

# 2 c) comando skills
@app.command()
def skills(job_title: str):
    job_url = f"https://www.ambitionbox.com/jobs/search?tag={job_title.replace(' ', '%20')}"
    typer.echo(f"A ver skills para: {job_title}")

    top_skills = get_top_skills(job_url)

    if top_skills:
        typer.echo(json.dumps({"top_skills": top_skills}, ensure_ascii=False))

        
        save = typer.confirm("Deseja salvar as informações no arquivo CSV?")
        if save:
            save_to_csv(top_skills, f"{job_title}_top_skills.csv")
        else:
            typer.echo("Informações não foram salvas.")
    else:
         typer.echo(json.dumps({"error": "Não foi possível encontrar as skills."}))

# 2 d) indeed daos
@app.command()
def getd(id:int):
    url = "https://api.itjobs.pt/job/get.json"
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
        company_info = get_company_info_indeed(company_name)
        if company_info:
            data.update(company_info)

    typer.echo(data)


if __name__ == "__main__":
    app()