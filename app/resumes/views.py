import subprocess
import os

from django.http import JsonResponse, FileResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from app.resumes.controllers import (ProfileController, EducationController, ExperienceController,
                                     ProjectController, AchievementController, SkillController, ProfileLinkController)
from app.resumes.serializers import (ProfileSerializer, EducationSerializer, ExperienceSerializer,
                                     ProjectSerializer, AchievementSerializer, SkillSerializer, ProfileLinkSerializer)
from app.resumes.schemas import (ProfileSchema, EducationSchema, ExperienceSchema,
                                 ProjectSchema, AchievementSchema, SkillSchema, ProfileLinkSchema, ResumeSchema)
from app.utils.views import BaseViewSet


class ResumeViewSet(BaseViewSet):
    # Profile
    profile_controller = ProfileController()
    profile_serializer = ProfileSerializer
    profile_schema = ProfileSchema

    # Education
    education_controller = EducationController()
    education_serializer = EducationSerializer
    education_schema = EducationSchema

    # Experience
    experience_controller = ExperienceController()
    experience_serializer = ExperienceSerializer
    experience_schema = ExperienceSchema

    # Project
    project_controller = ProjectController()
    project_serializer = ProjectSerializer
    project_schema = ProjectSchema

    # Achievement
    achievement_controller = AchievementController()
    achievement_serializer = AchievementSerializer
    achievement_schema = AchievementSchema

    # Skill
    skill_controller = SkillController()
    skill_serializer = SkillSerializer
    skill_schema = SkillSchema

    # ProfileLink
    profile_link_controller = ProfileLinkController()
    profile_link_serializer = ProfileLinkSerializer
    profile_link_schema = ProfileLinkSchema

    resume_schema = ResumeSchema

    @action(methods=['post'], detail=False, url_path='generate-pdf')
    def generate_pdf(self, request, *args, **kwargs):
        errors, data = self.profile_controller.parse_request(self.resume_schema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        output_dir = settings.BASE_DIR / "resumes_pdfs"
        #  clean before generating new pdf
        clean_directory(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_file_name = data.profile.email
        filled_resume_path = output_dir / f"{output_file_name}.tex"
        data_sets = {
            "education": data.education,
            "experience": data.experience,
            "project": data.project,
            "skill": data.skill,
            "achievement": data.achievement,
            "profile_links": data.profile_links,
        }

        fill_and_compile_latex_template(data.profile, data_sets, output_dir, filled_resume_path)
        pdf_file_path = output_dir / f"{output_file_name}.pdf"
        if not os.path.exists(pdf_file_path):
            return Response({"error": "PDF file not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use FileResponse to serve the PDF file
        return FileResponse(open(pdf_file_path, 'rb'), as_attachment=True, filename="resume.pdf")


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
            description_items = "\n".join([f"\\resumeItem{{{desc}}}" for desc in item.description])
            entry = f"""
            \\resumeSubHeadingListStart
                \\resumeSubheading
                {{{item.company}}}{{{item.duration}}}{{{item.role}}}{{{item.location}}}
                \\resumeItemListStart
                    {description_items}
                \\resumeItemListEnd
            \\resumeSubHeadingListEnd
            """
        elif section_template == "project":
            description_items = "\n".join([f"\\resumeItem{{{desc}}}" for desc in item.description])
            entry = f"""
            \\resumeSubHeadingListStart
                \\resumeProjectHeading
                {{{item.name}}}{{{item.duration}}}
                \\resumeItemListStart
                    {description_items}
                \\resumeItemListEnd
            \\resumeSubHeadingListEnd
            """
        elif section_template == "achievement":
            description_items = "\n".join([f"\\resumeItem{{{desc}}}" for desc in item.description])
            entry = f"""
            \\resumeSubHeadingListStart
                \\item
                \\textbf{{{item.name}}}
                \\resumeItemListStart
                    {description_items}
                \\resumeItemListEnd
            \\resumeSubHeadingListEnd
            """
        elif section_template == "skill":
            entry = f"\\item{{\\textbf{{{item.skill}}}: {item.value}}}"
        elif section_template == "education":
            entry = f"""
            \\resumeSubHeadingListStart
                \\resumeSubheading
                {{{item.institution}}}{{{item.location}}}
                {{{item.degree}}}{{{item.duration}}}
            \\resumeSubHeadingListEnd
            """
        entries += entry
    if section_template == "profile_links":
        link_items = [f"\\href{{{get_perfect_url(link.url)}}}{{\\text{{{link.platform}}}}} \\qquad" for link in data]
        # Concatenate all link items into a single LaTeX itemize environment
        entries += "\\begin{itemize}[leftmargin=0.15in, label={}]\n    " + "\n    ".join(
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


def fill_and_compile_latex_template(user_data, data_sets, output_dir, filled_resume_path):
    """Fill a LaTeX template with user data and compile it to a PDF."""
    env = Environment(loader=FileSystemLoader(settings.BASE_DIR), autoescape=False)
    template = env.get_template('resume_template.tex')

    render_data = user_data.dict()
    for section, data in data_sets.items():
        render_data[f"{section}_entries"] = prepare_latex_entry(data, section)

    filled_content = template.render(**render_data)
    with open(filled_resume_path, 'w') as file:
        file.write(filled_content)

    if not compile_latex_to_pdf(str(filled_resume_path), str(output_dir)):
        print("Failed to compile LaTeX to PDF.")
        # clean_directory(output_dir)
        return

    print(f"Resume PDF successfully generated at {filled_resume_path.with_suffix('.pdf')}")
