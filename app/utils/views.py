from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from app.utils.constants import Timeouts
from app.utils.helpers import build_cache_key, qdict_to_dict
from app.utils.pagination import MyPagination


class BaseViewSet(viewsets.ViewSet):
    controller = None
    serializer = None
    create_schema = None
    update_schema = None
    list_schema = None
    cache_key_retrieve = None
    cache_key_list = None

    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(self.create_schema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        errors, instance = self.controller.create(**data.dict())
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(data={"id": instance.pk}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(self.update_schema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        instance = self.controller.get_instance_by_pk(pk=pk)
        if not instance:
            return JsonResponse({"error": "Instance with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)

        errors, instance = self.controller.edit(instance_id=pk, **data.dict())
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(data={"id": instance.pk, "message": "Instance updated"}, status=status.HTTP_200_OK)

    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(self.list_schema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

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
                res = self.controller.serialize_queryset(page, self.serializer)
                if self.cache_key_list.value:
                    cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
                return paginator.get_paginated_response(res)
            res = self.controller.serialize_queryset(queryset, self.serializer)

        return JsonResponse(res, safe=False, status=status.HTTP_200_OK)

    def retrieve(self, request, pk, *args, **kwargs):
        instance, cache_key = None, ""
        if self.cache_key_retrieve.value:
            cache_key = self.cache_key_retrieve.value.format(pk=pk)
            instance = cache.get(cache_key)
        if instance:
            data = instance
        else:
            instance = self.controller.get_instance_by_pk(pk=pk)
            if not instance:
                return JsonResponse({"error": "Instance with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(instance, self.serializer)
            if self.cache_key_retrieve:
                cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def make_inactive(self, request, pk, *args, **kwargs):
        instance = self.controller.get_instance_by_pk(pk=pk)
        if not instance:
            return JsonResponse({"error": "Instance with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
        errors, _ = self.controller.make_inactive(instance)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(data={"message": "Successfully inactivated."}, status=status.HTTP_200_OK)
