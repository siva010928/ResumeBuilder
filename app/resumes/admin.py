from django.contrib import admin
from app.resumes.models import Resume, Profile, Education, Experience, Project, Achievement, Skill, ProfileLink


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


class ProfileLinkInline(admin.TabularInline):
    model = ProfileLink
    extra = 1


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at', 'updated_at')
    inlines = [
        ProfileInline,
        EducationInline,
        ExperienceInline,
        ProjectInline,
        AchievementInline,
        SkillInline,
        ProfileLinkInline,
    ]


# Optionally, register other models individually if needed for direct editing outside of the Resume context
@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('id', 'institution', 'location', 'course', 'duration', 'resume')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'company', 'location', 'duration', 'resume')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'duration', 'resume')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'resume')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'skill', 'value', 'resume')


@admin.register(ProfileLink)
class ProfileLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'platform', 'url', 'resume')
