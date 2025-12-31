from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import CustomUser, Role
from accounts.selectors.user_selectors import user_list, user_get
from accounts.services.user_services import (
    user_create, 
    user_update, 
    user_delete, 
    user_deactivate
)
from accounts.permissions import (IsAdminOrManager, 
    IsWorkStreamManager, 
    IsSchoolManager, 
    IsTeacher, 
    IsSecretary, 
    IsStaffUser,
    IsAdminOrManagerOrSecretary,
)
from django.core.exceptions import PermissionDenied


class UserListApi(APIView):
    permission_classes = [IsAdminOrManager]

    class FilterSerializer(serializers.Serializer):
        role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=False)
        search = serializers.CharField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        work_stream_name = serializers.CharField(source='work_stream.name', read_only=True)
        school_name = serializers.CharField(source='school.school_name', read_only=True)

        class Meta:
            model = CustomUser
            fields = [
                'id', 'email', 'full_name', 'role',
                'work_stream', 'work_stream_name',
                'school', 'school_name',
                'is_active', 'date_joined'
            ]

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        users = user_list(
            filters=filter_serializer.validated_data,
            user=request.user
        )
        
        data = self.OutputSerializer(users, many=True).data
        return Response(data)


class UserCreateApi(APIView):
    permission_classes = [IsStaffUser]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        full_name = serializers.CharField(max_length=150)
        role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)
        password = serializers.CharField(write_only=True)
        work_stream = serializers.IntegerField(required=False, allow_null=True)
        school = serializers.IntegerField(required=False, allow_null=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(
            creator=request.user,
            **serializer.validated_data
        )

        return Response(
            UserListApi.OutputSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class UserDetailApi(APIView):
    permission_classes = [IsStaffUser]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        full_name = serializers.CharField(max_length=150, required=False)
        role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=False)
        work_stream = serializers.IntegerField(required=False, allow_null=True)
        school = serializers.IntegerField(required=False, allow_null=True)
        is_active = serializers.BooleanField(required=False)

    def get(self, request, user_id):
        user = user_get(user_id=user_id,actor=request.user)
        return Response(UserListApi.OutputSerializer(user).data)

    def patch(self, request, user_id):
        user = user_get(user_id=user_id, actor=request.user)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if request.user.role == CustomUser.Role.ADMIN:
            pass

        # WORKSTREAM MANAGER
        elif request.user.role == CustomUser.Role.MANAGER_WORKSTREAM:
            data.pop("role", None)
            data.pop("work_stream", None)

            if "school" in data:
                if user.work_stream_id != request.user.work_stream_id:
                    raise PermissionDenied(
                        "You can only move users inside your own workstream."
                    )

        else:
            data.pop("role", None)
            data.pop("work_stream", None)
            data.pop("school", None)

        user = user_update(user=user, data=data)

        return Response(
            UserListApi.OutputSerializer(user).data,
            status=status.HTTP_200_OK
        )


    def delete(self, request, user_id):
        raise PermissionDenied("Use deactivate instead of delete.")
        # user = user_get(user_id=user_id,actor=request.user)
        # user_delete(user=user)
        # return Response(status=status.HTTP_204_NO_CONTENT)


class UserDeactivateApi(APIView):
    permission_classes = [IsAdminOrManagerOrSecretary]
    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response(
                {"detail": "You cannot deactivate yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user_get(user_id=user_id,actor=request.user)
        user_deactivate(user=user)
        return Response({"detail": "User deactivated successfully."}, status=status.HTTP_200_OK)
