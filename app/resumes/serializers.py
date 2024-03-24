from django.db import transaction
from rest_framework import serializers
from .models import Education, Experience, Project, Skill, Achievement, ProfileLink, Resume, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('id', 'resume')


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ('id', 'resume')


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        exclude = ('id', 'resume')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ('id', 'resume')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        exclude = ('id', 'resume')


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        exclude = ('id', 'resume')


class ProfileLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileLink
        exclude = ('id', 'resume')


class ResumeDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    skills = SkillSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    profile_links = ProfileLinkSerializer(many=True, required=False)

    class Meta:
        model = Resume
        fields = ['id', 'title', 'profile', 'educations', 'experiences',
                  'projects', 'skills', 'achievements', 'profile_links']

    def create(self, validated_data):
        title = validated_data.get('title')
        profile_data = validated_data.get('profile')
        educations_data = validated_data.get('educations', [])
        experiences_data = validated_data.get('experiences', [])
        projects_data = validated_data.get('projects', [])
        skills_data = validated_data.get('skills', [])
        achievements_data = validated_data.get('achievements', [])
        profile_links_data = validated_data.get('profile_links', [])

        resume = Resume.objects.create(user=self.context['user'], title=title)
        Profile.objects.create(resume=resume, **profile_data)

        for education_data in educations_data:
            Education.objects.create(resume=resume, **education_data)
        for experience_data in experiences_data:
            Experience.objects.create(resume=resume, **experience_data)
        for project_data in projects_data:
            Project.objects.create(resume=resume, **project_data)
        for skill_data in skills_data:
            Skill.objects.create(resume=resume, **skill_data)
        for achievement_data in achievements_data:
            Achievement.objects.create(resume=resume, **achievement_data)
        for profile_link_data in profile_links_data:
            ProfileLink.objects.create(resume=resume, **profile_link_data)

        return resume

    def update(self, instance, validated_data):
        with transaction.atomic():
            profile_data = validated_data.get('profile')
            educations_data = validated_data.get('educations', [])
            experiences_data = validated_data.get('experiences', [])
            projects_data = validated_data.get('projects', [])
            skills_data = validated_data.get('skills', [])
            achievements_data = validated_data.get('achievements', [])
            profile_links_data = validated_data.get('profile_links', [])

            # Update the Resume instance
            instance.title = validated_data.get('title', instance.title)
            instance.save()

            # Delete and recreate related objects
            # Profile (OneToOne)
            if hasattr(instance, 'profile'):
                instance.profile.delete()
            Profile.objects.create(resume=instance, **profile_data)

            # Educations, Experiences, etc. (ForeignKey related objects)
            self.recreate_related_objects(Education, educations_data, instance)
            self.recreate_related_objects(Experience, experiences_data, instance)
            self.recreate_related_objects(Project, projects_data, instance)
            self.recreate_related_objects(Skill, skills_data, instance)
            self.recreate_related_objects(Achievement, achievements_data, instance)
            self.recreate_related_objects(ProfileLink, profile_links_data, instance)

            return instance

    def recreate_related_objects(self, model, data, resume_instance):
        """
        Helper method to delete and recreate related objects for a given model.
        """
        # Delete existing related objects
        model.objects.filter(resume=resume_instance).delete()
        # Recreate related objects with new data
        for item_data in data:
            model.objects.create(resume=resume_instance, **item_data)
