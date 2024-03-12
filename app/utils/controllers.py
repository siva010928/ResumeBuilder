from django.db.utils import IntegrityError
from pydantic import ValidationError
from app.utils.helpers import get_serialized_exception


class Controller:

    def __init__(self, model, serializer_class):
        self.model = model
        self.serializer_class = serializer_class

    def create(self, **kwargs):
        try:
            instance = self.model.objects.create(**kwargs)
            return None, instance
        except (IntegrityError, ValueError) as e:
            return get_serialized_exception(e)

    def edit(self, instance_id, **kwargs):
        try:
            instance = self.model.objects.get(id=instance_id)
            for attr, value in kwargs.items():
                setattr(instance, attr, value)
            instance.save()
            return None, instance
        except (IntegrityError, ValueError) as e:
            return get_serialized_exception(e)

    def filter(self, **filters):
        instance_qs = self.model.objects.all()
        for attr, value in filters.items():
            if value is not None:
                instance_qs = instance_qs.filter(**{attr: value})
        return None, instance_qs

    # def parse_request(self, request_schema, data):
    #     try:
    #         parsed_request = request_schema(**data)
    #         if issubclass(request_schema, BaseSchemaListingReqSchema):
    #             parsed_request.get_start_time()
    #             parsed_request.get_end_time()
    #         return None, parsed_request
    #     except (ValidationError, ValueError) as e:  # Catch both Pydantic's ValidationError and ValueError
    #         # The error messages can be combined or handled separately as needed
    #         return {"errors": e.errors() if isinstance(e, ValidationError) else str(e)}, None

    def parse_request(self, request_schema, data):
        try:
            return None, request_schema(**data)
        except (ValidationError, ValueError, TypeError) as e:  # Catch both Pydantic's ValidationError and ValueError
            # The error messages can be combined or handled separately as needed
            return {"errors": str(e)}, None

    def get_instance_by_pk(self, pk: int):
        try:
            instance = self.model.objects.get(pk=pk)
            return instance
        except self.model.DoesNotExist as e:
            return None

    def serialize_one(self, obj):
        data = self.serializer_class(obj).data
        return data

    def serialize_queryset(self, obj_list):
        data = []
        for obj in obj_list:
            data.append(self.serialize_one(obj))
        return data

    def make_inactive(self, obj):
        try:
            obj.is_active = False
            obj.save()
        except (IntegrityError, ValueError) as e:
            return get_serialized_exception(e)
        return None, True
