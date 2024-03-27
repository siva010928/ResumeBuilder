import re
import subprocess
import os

from django.contrib.auth import get_user_model
from django.core import cache
from django.http import JsonResponse, FileResponse, HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from app.resumes.controllers import (ProfileController, EducationController, ExperienceController,
                                     ProjectController, AchievementController, SkillController, ProfileLinkController,
                                     ResumeController)
from app.resumes.models import Resume
from app.resumes.serializers import (ProfileSerializer, EducationSerializer, ExperienceSerializer,
                                     ProjectSerializer, AchievementSerializer, SkillSerializer, ProfileLinkSerializer,
                                     ResumeDetailSerializer)
from app.resumes.schemas import (ProfileSchema, EducationSchema, ExperienceSchema,
                                 ProjectSchema, AchievementSchema, SkillSchema, ProfileLinkSchema, ResumeSchema,
                                 ResumeDynamicSchema, ResumeListSchema)
from app.utils.constants import CacheKeys, Timeouts
from app.utils.helpers import build_cache_key
from app.utils.pagination import MyPagination
from app.utils.views import BaseViewSet

User = get_user_model()


class ResumeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    controller = ResumeController()
    list_schema = ResumeListSchema
    resume_schema = ResumeSchema
    resume_dynamic_schema = ResumeDynamicSchema
    cache_key_retrieve = CacheKeys.RESUME_DETAILS_BY_PK
    cache_key_list = CacheKeys.RESUME_LIST

    @extend_schema(
        description="List all Resumes",
        responses={200: ResumeDetailSerializer(many=True)},
        parameters=[
            OpenApiParameter(name='user_id', type=int, description='Filter by user ID')
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, **kwargs)

    @extend_schema(
        description="List allmy  Resumes",
        responses={200: ResumeDetailSerializer(many=True)},
    )
    @action(methods=['get'], detail=False, url_path='my-resumes')
    def my_resumes(self, request, *args, **kwargs):
        data = self.list_schema(user_id=request.user.id)
        paginator = MyPagination()
        page_key = request.query_params.get('page')
        instance, cache_key = None, ""
        if self.cache_key_list.value:
            cache_key = build_cache_key(
                self.cache_key_list,
                page=page_key,
                **data.dict()
            )
            instance = cache.get(cache_key)

        if instance:
            res = instance
        else:
            errors, data = self.controller.filter(**data.dict())
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            queryset = data  # Assuming data is a queryset here
            page = paginator.paginate_queryset(queryset, request, view=self)
            if page is not None:
                res = self.controller.serialize_queryset(page)
                if self.cache_key_list.value:
                    cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
                return paginator.get_paginated_response(res)
            res = self.controller.serialize_queryset(queryset)

        return JsonResponse(res, safe=False, status=status.HTTP_200_OK)

    @extend_schema(
        description="Retrieve a specific Resume by ID",
        responses={200: ResumeDetailSerializer}
    )
    def retrieve(self, request, pk=None, *args, **kwargs):
        return super().retrieve(request, pk, *args, **kwargs)

    @action(methods=['post'], detail=False, url_path='generate-pdf', permission_classes=[AllowAny])
    def generate_pdf(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(self.resume_schema, request.data)
        return self.get_pdf(errors, data, None)

    def get_pdf(self, errors, data, resume_id):
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        output_dir = settings.BASE_DIR / "resumes_pdfs"
        #  clean before generating new pdf
        clean_directory(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_file_name = data.profile.email
        filled_resume_path = output_dir / f"{output_file_name}.tex"
        data_sets = {
            "education": data.educations,
            "experience": data.experiences,
            "project": data.projects,
            "skill": data.skills,
            "achievement": data.achievements,
            "profile_links": data.profile_links,
        }

        fill_and_compile_latex_template(data.profile, data_sets, output_dir, filled_resume_path)
        pdf_file_path = output_dir / f"{output_file_name}.pdf"
        if not os.path.exists(pdf_file_path):
            return Response({"error": "PDF file not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use FileResponse to serve the PDF file
        # return FileResponse(open(pdf_file_path, 'rb'), as_attachment=True, filename="resume.pdf")

        with open(pdf_file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
            if resume_id:
                response['X-Resume-ID'] = resume_id
            return response

    @action(detail=False, methods=['post'], url_path='process-resume')
    def process_resume(self, request, *args, **kwargs):
        user = request.user
        user = User.objects.filter(email='siva010928@gmail.com').first()
        serializer = ResumeDetailSerializer(data=request.data, context={'user': user})

        if serializer.is_valid():
            resume_id = request.data.get('id', None)

            if resume_id:
                # Updating an existing resume
                try:
                    resume = Resume.objects.get(id=resume_id, user=user)
                    updated_resume = serializer.update(resume, serializer.validated_data)
                except Resume.DoesNotExist:
                    return Response({"error": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Creating a new resume
                updated_resume = serializer.create(serializer.validated_data)

            resume_id = updated_resume.id
            errors, data = self.controller.parse_request(self.resume_dynamic_schema, request.data)
            return self.get_pdf(errors, data, resume_id)
            # return self.get_pdf(None, serializer.validated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            description_items = "\n".join([f"\\resumeItem{{{escape_latex(desc)}}}" for desc in item.description])
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
            description_items = "\n".join([f"\\resumeItem{{{escape_latex(desc)}}}" for desc in item.description])
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
            description_items = "\n".join([f"\\resumeItem{{{escape_latex(desc)}}}" for desc in item.description])
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
    if settings.DEPLOYMENT_ENVIRONMENT == "prod":
        command = ["pdflatex", "-interaction=nonstopmode", "-output-directory", output_dir, tex_file]
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


def escape_latex(value):
    """Escapes LaTeX special characters in a string using a precompiled regex."""
    # Regular expression pattern for LaTeX special characters
    regex_pattern = re.compile(r'([&%$#_{}~^\\<>])')

    # Replacement function
    def replace(match):
        char = match.group(0)
        return {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}',
            '\\': '\\textbackslash{}',
            '<': '\\textless{}',
            '>': '\\textgreater{}',
        }.get(char, char)

    return regex_pattern.sub(replace, value)


def fill_and_compile_latex_template(user_data, data_sets, output_dir, filled_resume_path):
    """Fill a LaTeX template with user data and compile it to a PDF."""
    env = Environment(loader=FileSystemLoader(settings.BASE_DIR), autoescape=False)
    template = env.get_template('resume_template.tex')

    render_data = user_data.dict()
    for section, data in data_sets.items():
        has_content = len(data) > 0  # Check if the section has content
        render_data[f"has_{section}_content"] = has_content  # Add a flag to indicate if there's content
        if has_content:
            render_data[f"{section}_entries"] = prepare_latex_entry(data, section)

    filled_content = template.render(**render_data)
    with open(filled_resume_path, 'w') as file:
        file.write(filled_content)

    if not compile_latex_to_pdf(str(filled_resume_path), str(output_dir)):
        print("Failed to compile LaTeX to PDF.")
        return

    print(f"Resume PDF successfully generated at {filled_resume_path.with_suffix('.pdf')}")
