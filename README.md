# Gitmail Harvester

Gitmail Harvester is a powerful OSINT/Red Team and Pentest tool designed to extract email addresses from commit history in GitHub repositories (GitLab support will be added later). It provides a convenient way to gather email addresses from public  repositories of users or organizations, offering support for the GitHub platform.


![demo](img/demo.gif)



## Features

- Support for GitHub (GitLab functionality will be added later).
- Ability to extract from both user and organization repositories.
- Authentication support to increase rate limits and access private repositories.
- Automatically generates output in JSON, CSV, and plain text formats.
- Customizable output file naming.
- Beautiful HTML report.


## Requirements

- Python 3.x
- Requests library (`pip install requests`)
- Progressbar library (`pip install progressbar2`)
- Rich library (`pip install rich`)

## Installation

Clone this repository to your local machine using:

```bash
git clone https://github.com/Imp0sters/Gitmail-Harvester/
cd Gitmail-Harvester
```

Ensure you have Python 3 installed, and then install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

The tool can be executed from the command line with various options to specify the target platform, username or organization.

### Basic Syntax

```bash
python3 GitMailharvester.py [OPTIONS]
```

### Options

- `-s, --service`: **Required.** The hosting service (currently only `github` is supported).
- `-u, --username`: The GitHub username for which to fetch repositories.
- `-o, --organisation`: The GitHub organization for which to fetch repositories.
- `-ghT, --github-token`: The GitHub personal access token for increased rate limits and private repo access.
- `-d, --debug`: Enable debug mode to print all requests.

### Examples

1. Extract all committers from a GitHub user's repositories and generate output files:

```bash
python GitMailharvester.py -s github -u username -ghT YOUR_GITHUB_TOKEN
```

2. Extract all committers from a GitHub organization's repositories and generate output files:

```bash
python GitMailharvester.py -s github -o organisation_name -ghT YOUR_GITHUB_TOKEN
```

### Output

The tool automatically generates output in the following formats:

- **JSON** (`username_emails.json` or `organisation_emails.json`)
- **CSV** (`username_emails.csv` or `organisation_emails.csv`)
- **Plain text** (`username_emails.txt` or `organisation_emails.txt`)
- **HTML report** 

### Notes

- Replace `YOUR_GITHUB_TOKEN` with your actual personal access token from GitHub.
- The personal access token is necessary for accessing private repositories and avoiding rate limits on API requests.
- GitLab support will be added later, so only GitHub is functional for now.

### Progress Tracking

- The tool provides real-time feedback using progress bars for both repository and commit extraction processes.
- Log messages, such as "Fetching commits for repository 'X'", are shown in green to indicate important steps in the process.

