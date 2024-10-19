#!/usr/bin/env python3
# File name          : gitmailharvester.py
# Author             : bl4ckarch & gr0bot
# Date created       : 6 feb 2024

import sys
import argparse
import requests
import csv
import json
import logging
import webbrowser
import os
import progressbar 
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
import datetime

console = Console()

logging.basicConfig(level=logging.INFO, handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger()

def pop_err(text):
    logger.error(text)
    sys.exit()

def pop_dbg(text):
    logger.debug(text)

def pop_info(text):
    logger.info(text)

def pop_valid(text):
    console.print(f"[bold green]{text}[/bold green]")

def make_api_call(url, headers=None, debug=False):
    if debug:
        pop_dbg(f"Making request to URL: {url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            pop_err(f"⛔ URL not found: {url}")
        elif response.status_code == 403:
            pop_err("⛔ API rate limit exceeded.")
        elif response.status_code == 200:
            return response.json()
        else:
            pop_err(f"⛔ Failed to access {url} with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        pop_err(f"⛔ Request failed: {e}")
    return None

def get_repos(service, name, entity_type, token, debug=False):
    repos = []
    if service == 'github':
        api_url = f'https://api.github.com/users/{name}/repos' if entity_type == 'user' else f'https://api.github.com/orgs/{name}/repos'
        headers = {'Authorization': f'token {token}'} if token else {}
        repos_data = make_api_call(api_url, headers, debug)
        if repos_data is not None:
        
            pop_valid("⚙️ Fetching repositories...")
            with progressbar.ProgressBar(max_value=len(repos_data)) as bar:
                for i, repo in enumerate(repos_data):
                    repos.append(repo['name'])
                    bar.update(i + 1)
    else:
        pop_info("⚠️ Service not supported")
    return repos

def get_commits(service, name, repo_name, token, debug=False):
    commits = []
    if service == 'github':
        api_url = f'https://api.github.com/repos/{name}/{repo_name}/commits'
        headers = {'Authorization': f'token {token}'} if token else {}
        commits_data = make_api_call(api_url, headers, debug)
        if commits_data is not None:
            # Initialize progress bar for commits
            with progressbar.ProgressBar(max_value=len(commits_data)) as bar:
                for i, commit in enumerate(commits_data):
                    committer_info = commit['commit']['committer']
                    commits.append({'name': committer_info['name'], 'email': committer_info['email']})
                    bar.update(i + 1)
    else:
        pop_info("⚠️ Service not supported")
    return commits

def write_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def write_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

def write_to_txt(data, filename):
    with open(filename, 'w') as txtfile:
        for entry in data:
            txtfile.write(f"{entry['name']}: {entry['email']}\n")



def create_html(data, filename, entity_name):
    logo_url = "https://avatars.githubusercontent.com/u/166144105?s=200&v=4"
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
    <html>
    <head>
        <title>Emails from {entity_name} repository commits</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #001f3f;  /* Navy blue */
                color: white;
                margin: 0;
                padding: 0;
            }}
            .navbar {{
                background-color: #001f3f;
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                position: fixed;
                top: 0;
                width: 100%;
                z-index: 1000;
                border-bottom: 2px solid #0074D9;
            }}
            .navbar h1 {{
                margin: 0;
                color: white;
            }}
            .logo {{
                width: 60px;
                height: 60px;
            }}
            h1 {{
                text-align: center;
                padding: 80px 20px 20px 20px;
                color: white;
            }}
            table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
                margin-top: 60px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
                color: white;
            }}
            th {{
                background-color: #0074D9;
            }}
            tr:nth-child(even) {{
                background-color: #003366;
            }}
            tr:hover {{
                background-color: #0074D9;
            }}
            footer {{
                text-align: center;
                padding: 20px;
                background-color: #001f3f;
                color: white;
                position: fixed;
                width: 100%;
                bottom: 0;
            }}
            .content {{
                padding-top: 150px;  /* To prevent overlap with the fixed navbar */
                padding-bottom: 60px; /* Prevent overlap with the footer */
            }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <h1 style="width: 706.233px;padding-top: 19px;">Emails from {entity_name} repository commits</h1>
            <img src="{logo_url}" alt="Logo" class="logo" style="margin-right: 100px;">
        </div>
        <div class="content">
            <table>
              <thead>
                    <tr><th>Name</th><th>Email</th></tr>
                </thead>
                <tbody>
    """
    for entry in data:
        html_content += f"<tr><td>{entry['name']}</td><td>{entry['email']}</td></tr>"
    
    html_content += f"""
                </tbody>
            </table>
        </div>
        <footer>
            Generated by Gitmail Harvester on {current_date}
        </footer>
    </body>
    </html>
    """
    
        with open(filename, 'w') as htmlfile:
        htmlfile.write(html_content)
    
        abs_path = os.path.abspath(filename)
    
        webbrowser.open(f'file://{abs_path}')


def deduplicate_commiters(commiters):
    unique_commiters = {c['email']: c for c in commiters}.values()
    return list(unique_commiters)

def main():
    parser = argparse.ArgumentParser(
        prog='gitmailharvester',
        description='Tool for extracting e-mail addresses from commits in a GitHub account.',
        epilog='''Examples:
            python gitmailharvester.py --service github --username john_doe --organisation my_org --github-token yourtokenhere
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-s', '--service', choices=['github'], required=True, help='Service (only "github" supported).')
    parser.add_argument('-u', '--username', help='Username for the service. Used to fetch user repositories.')
    parser.add_argument('-o', '--organisation', help='Organisation name for the service. Used to fetch organisation repositories.')
    parser.add_argument('-ghT', '--github-token', help='GitHub personal access token. Required for accessing private repositories or increasing rate limits.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode to print all requests.')
    
    args = parser.parse_args()

        if args.debug:
        logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])
    else:
        logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])

        if not args.username and not args.organisation:
        pop_err("⛔ Either --username or --organisation must be provided.")
    
        entity_type = 'user' if args.username else 'org'
    name = args.username if args.username else args.organisation
    token = args.github_token

        pop_valid("⚙️ Now searching for emails...")

        repos = get_repos(args.service, name, entity_type, token, args.debug)
    if not repos:
        pop_err(f"⛔ No repositories found for {name}.")

    commiters = []
    for repo in repos:
        pop_valid(f"⚙️ Fetching commits for repository '{repo}'...")
        commiters.extend(get_commits(args.service, name, repo, token, args.debug))

    if not commiters:
        pop_err(f"⚠️ No commit data found for {name}.")

        unique_commiters = deduplicate_commiters(commiters)

        output_filename_base = f"{name}_emails"
    write_to_csv(unique_commiters, f"{output_filename_base}.csv")
    pop_valid(f"✅ Data written to {output_filename_base}.csv")

    write_to_json(unique_commiters, f"{output_filename_base}.json")
    pop_valid(f"✅ Data written to {output_filename_base}.json")

    write_to_txt(unique_commiters, f"{output_filename_base}.txt")
    pop_valid(f"✅ Data written to {output_filename_base}.txt")

        create_html(unique_commiters, "output.html", name)
    pop_valid("✅ HTML report created and opened in browser.")

if __name__ == '__main__':
    banner_text = """
     ██████╗ ██╗████████╗███╗   ███╗ █████╗ ██╗██╗         ██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗███████╗██████╗ 
    ██╔════╝ ██║╚══██╔══╝████╗ ████║██╔══██╗██║██║         ██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
    ██║  ███╗██║   ██║   ██╔████╔██║███████║██║██║         ███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║   █████╗  ██████╔╝
    ██║   ██║██║   ██║   ██║╚██╔╝██║██╔══██║██║██║         ██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   ██╔══╝  ██╔══██╗
    ╚██████╔╝██║   ██║   ██║ ╚═╝ ██║██║  ██║██║███████╗    ██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║   ███████╗██║  ██║
     ╚═════╝ ╚═╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
    
    
    Made with ❤️  by @gr0bot and @bl4ckarch
    """
    console.print(Text(banner_text, style="cyan"))
    pop_valid("✅ Gitmail Harvester started...")
    main()
