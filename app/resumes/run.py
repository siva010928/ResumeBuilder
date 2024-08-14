import subprocess
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def get_perfect_url(url):
    """Prepend 'https://' to URLs that lack a scheme."""
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def prepare_latex_entry(data, section_template):
    entries = ""
    entry = ""
    for item in data:
        if section_template == "experience":
            description_items = "\n".join([f"\\resumeItem{{{desc}}}" for desc in item['description']])
            entry = f"""
            \\resumeSubHeadingListStart
                \\resumeSubheading
                {{{item['company']}}}{{{item['duration']}}}{{{item['role']}}}{{{item['location']}}}
                \\resumeItemListStart
                    {description_items}
                \\resumeItemListEnd
            \\resumeSubHeadingListEnd
            """
        elif section_template == "project":
            description_items = "\n".join([f"\\resumeItem{{{desc}}}" for desc in item['description']])
            entry = f"""
            \\resumeSubHeadingListStart
                \\resumeSubheading
                {{{item['name']}}}{{{item['duration']}}}
                \\resumeItemListStart
                    {description_items}
                \\resumeItemListEnd
            \\resumeSubHeadingListEnd
            """
        elif section_template == "achievement":
            description_items = "\n".join([f"\\resumeItem{{{desc}}}" for desc in item['description']])
            entry = f"""
            \\resumeSubHeadingListStart
                \\item
                \\textbf{{{item['name']}}}
                \\resumeItemListStart
                    {description_items}
                \\resumeItemListEnd
            \\resumeSubHeadingListEnd
            """
        elif section_template == "skill":
            entry = f"\\item{{\\textbf{{{item['skill']}}}: {item['value']}}}"
        elif section_template == "education":
            entry = f"""
            \\resumeSubHeadingListStart
                \\resumeSubheading
                {{{item['institution']}}}{{{item['location']}}}
                {{{item['degree']}}}{{{item['duration']}}}
            \\resumeSubHeadingListEnd
            """
        entries += entry
    if section_template == "profile_links":
        link_items = []
        for link in data:
            # Check if the URL already starts with "http://" or "https://", if not, prepend "https://"
            url = get_perfect_url(link['url'])

            # Format the LaTeX command for the link
            link_item = f"\\href{{{url}}}{{\\text{{{link['platform']}}}}} \\qquad"
            link_items.append(link_item)

        # Concatenate all link items into a single LaTeX itemize environment
        entries = "\\begin{itemize}[leftmargin=0.15in, label={}]\n    " + "\n    ".join(
            link_items) + "\n \\end{itemize}"
    return entries


def compile_latex_to_pdf(tex_file, output_dir):
    """Compile a LaTeX file to PDF using pdflatex."""
    pdflatex_path = r"C:\texlive\2023\bin\windows\pdflatex.exe"  # Use the path found with `where pdflatex`
    command = [pdflatex_path, "-interaction=nonstopmode", "-output-directory", output_dir, tex_file]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error compiling LaTeX file {tex_file}:")
        print(result.stdout)
        print(result.stderr)
        return False
    return True


def clean_directory(directory):
    """Remove all files in the directory."""
    for item in directory.iterdir():
        if item.is_file():
            item.unlink()


def fill_and_compile_latex_template(user_data, data_sets):
    """Fill a LaTeX template with user data and compile it to a PDF."""
    env = Environment(loader=FileSystemLoader(BASE_DIR), autoescape=False)
    template = env.get_template('resume_template.tex')

    render_data = user_data.copy()
    for section, data in data_sets.items():
        render_data[f"{section}_entries"] = prepare_latex_entry(data, section)

    filled_content = template.render(**render_data)
    output_dir = BASE_DIR / "resumes_pdfs"
    output_dir.mkdir(exist_ok=True)
    filled_resume_path = output_dir / 'filled_resume.tex'
    with open(filled_resume_path, 'w') as file:
        file.write(filled_content)

    if not compile_latex_to_pdf(str(filled_resume_path), str(output_dir)):
        print("Failed to compile LaTeX to PDF.")
        # clean_directory(output_dir)
        return

    print(f"Resume PDF successfully generated at {filled_resume_path.with_suffix('.pdf')}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # Simulated request body data
    user_info = {
        "first_name": "Siva Prakash",
        "last_name": "Kumar",
        "location": "Coimbatore",
        "phone": "123-456-7890",
        "email": "jake@su.edu",
        "linkedin_username": "siva010928",
    }

    education_data = [
        {
            "institution": "Southwestern University",
            "location": "Georgetown, TX",
            "degree": "Bachelor of Arts in Computer Science, Minor in Business",
            "duration": "Aug. 2018 -- May 2021"
        },
        {
            "institution": "Blinn College",
            "location": "Bryan, TX",
            "degree": "Associate's in Liberal Arts",
            "duration": "Aug. 2014 -- May 2018"
        }
    ]

    experience_data = [
        {
            "role": "Undergraduate Research Assistant",
            "company": "Texas AM University",
            "location": "College Station, TX",
            "duration": "June 2020 -- Present",
            "description": [
                "Developed a REST API using FastAPI and PostgreSQL to store data from learning management systems",
                "Developed a full-stack web application using Flask, React, PostgreSQL, and Docker to analyze GitHub data",
                "Explored ways to visualize GitHub collaboration in a classroom setting"
            ]
        }
    ]

    project_data = [
        {
            "name": "Gitlytics",
            "duration": "June 2020 -- Present",
            "description": [
                "Developed a full-stack web application with Flask serving a REST API with React as the frontend",
                "Implemented GitHub OAuth to get data from user’s repositories",
                "Visualized GitHub data to show collaboration",
                "Used Celery and Redis for asynchronous tasks"
            ]
        }
    ]

    skill_data = [
        {
            "skill": "Languages",
            "value": "Java, Python, C/C++, SQL (Postgres), JavaScript, HTML/CSS, R"
        },
        {
            "skill": "Frameworks",
            "value": "React, Node.js, Flask, JUnit, WordPress, Material-UI, FastAPI"
        }
    ]

    achievement_data = [
        {
            "name": "Best Undergraduate Research Award",
            "description": [
                "Awarded for outstanding research in computer science department",
                "Focused on machine learning and data analysis"
            ]
        }
    ]

    profile_links_data = [
        {"platform": "Github", "url": "https://github.com/siva010928"},
        {"platform": "LinkedIn", "url": "https://linkedin.com/in/siva010928/"},
        {"platform": "HackerRank", "url": "https://hackerrank.com/siva010928"}
    ]

    # Organize your data sets here
    data_sets = {
        "education": education_data,
        "experience": experience_data,
        "project": project_data,
        "skill": skill_data,
        "achievement": achievement_data,
        "profile_links": profile_links_data,
    }

    fill_and_compile_latex_template(user_info, data_sets)
