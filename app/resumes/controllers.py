# Assuming serializers.py contains all necessary serializers
from app.resumes.serializers import ProfileSerializer, EducationSerializer, ExperienceSerializer, ProjectSerializer, \
    AchievementSerializer, SkillSerializer, ProfileLinkSerializer
from app.resumes.models import Profile, Education, Experience, Project, Achievement, Skill, ProfileLink
from app.utils.controllers import Controller


class ProfileController(Controller):
    def __init__(self):
        super().__init__(model=Profile, serializer_class=ProfileSerializer)


class EducationController(Controller):
    def __init__(self):
        super().__init__(model=Education, serializer_class=EducationSerializer)


class ExperienceController(Controller):
    def __init__(self):
        super().__init__(model=Experience, serializer_class=ExperienceSerializer)


class ProjectController(Controller):
    def __init__(self):
        super().__init__(model=Project, serializer_class=ProjectSerializer)


class AchievementController(Controller):
    def __init__(self):
        super().__init__(model=Achievement, serializer_class=AchievementSerializer)


class SkillController(Controller):
    def __init__(self):
        super().__init__(model=Skill, serializer_class=SkillSerializer)


class ProfileLinkController(Controller):
    def __init__(self):
        super().__init__(model=ProfileLink, serializer_class=ProfileLinkSerializer)
