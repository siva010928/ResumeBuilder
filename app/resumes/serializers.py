from rest_framework import serializers
from app.resumes.models import Profile, Education, Experience, Project, Achievement, Skill, ProfileLink


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['id', 'user']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ['id', 'user']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        exclude = ['id', 'user']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ['id', 'user']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        exclude = ['id', 'user']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        exclude = ['id', 'user']


class ProfileLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileLink
        exclude = ['id', 'user']
