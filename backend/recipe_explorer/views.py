from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, FavoriteSerializer
from rest_framework import status, generics
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.shortcuts import get_object_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

import requests
from django.http import JsonResponse

from .helper.dummy_response import res_1, res_2, res_3, res_4

from recipe_explorer.models import FavoriteModel

class LogIn(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    demo_username = "demo_user1"

    def post(self, request):
        is_demo = request.data['isDemo']

        try:
            if is_demo:
                user = get_object_or_404(User, username=self.demo_username)
            else:
                user = get_object_or_404(User, username=request.data['username'])

            if not is_demo and not user.check_password(request.data['password']):
                return Response(
                    {"detail":"User Not Found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(instance=user)

            return Response({"token":token.key, "user":serializer.data})
        
        except Exception:
            return Response(
                {"Message":"Error In Log In"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class UserDemo(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    demo_username = "demo_user1"

    def get(self, request):
        try:
            user_id = Token.objects.get(key=request.auth.key).user_id
            user = User.objects.get(pk=user_id)

            if not user:
                return Response(
                    {"message":"User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            is_user_demo = False
            
            if user.username == self.demo_username:
                is_user_demo = True

            return Response(
                {"data" : is_user_demo}, 
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            return Response(
                {"Message":"Error In Log In"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SignUp(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)

            return Response({"token":token.key, "user":serializer.data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogOut(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass

        return Response(
            {"Success":"Success Log Out"},
            status=status.HTTP_200_OK
        )
    
class RecipeExplorer(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            recipe_api = getattr(settings, "RECIPE_API", None)
            recipe_api_key = getattr(settings, "RECIPE_API_KEY", None)

            keywords = ""
            if request.GET.get("keyword") is not None:
                keywords = request.GET.get("keyword")

            search_recipe_url = (recipe_api.replace("{query}", keywords)).replace("{apiKey}", recipe_api_key)

            # return JsonResponse(res_1)
            response = requests.get(search_recipe_url)
            data = response.json()

            return JsonResponse(data)
        
        except :
            return Response(
                { "Error":"Something wrong" },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class Profile(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)

        if not user:
            return Response(
                {
                    "message":"User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer_user = self.serializer_class(instance=user)

        return Response({"user":serializer_user.data})

    def post(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)

        if user is not None:
            serializer_user = self.serializer_class(user, data=request.data, partial=True)

            if  serializer_user.is_valid():
                serializer_user.save()

                return Response(status=status.HTTP_200_OK)
            
        return Response(serializer_user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)

        if not user:
            return Response(
                {
                    "status": "fail",
                    "message": "User with not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class Favorite(generics.GenericAPIView):
    serializer_class = FavoriteSerializer
    queryset = FavoriteModel.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_all_favorite(self, user_id):
        try:
            return FavoriteModel.objects.filter(user_id=user_id)
        except:
            return None

    def post(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        user = User.objects.get(pk=user_id)

        if user is not None:
            favorite_data = self.queryset.filter(recipe_id=request.data['recipe_id'], user_id=user_id)

            if not favorite_data:
                serializer = self.serializer_class(data={"user":user_id, "recipe_id":request.data['recipe_id'], "title":request.data['title'], "imageURL":request.data['imageURL']})

                if  serializer.is_valid():
                    serializer.save()

                    return Response(status=status.HTTP_200_OK)
            
        return Response(
                {
                    "message":"Data already stored"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        user_id = Token.objects.get(key=request.auth.key).user_id
        favorite_response = self.get_all_favorite(user_id)
        
        if favorite_response is not None:
            serializer = self.serializer_class(favorite_response, many=True)

            return Response(serializer.data)
    
        return Response(
                {
                    "message":"User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

class RecipeDetail(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            recipe_api = getattr(settings, "RECIPE_DETAIL_RECIPE_API", None)
            recipe_api_key = getattr(settings, "RECIPE_API_KEY", None)
            recipe_id = request.GET.get("recipe_id")

            detail_recipe_url = (recipe_api.replace("{recipe_id}", recipe_id)).replace("{apiKey}", recipe_api_key)

            response = requests.get(detail_recipe_url)
            data = response.json()

            set_ingredient = {"ingredients" : ""}
            list_ingredient = []
            
            for item in data['extendedIngredients']:
                list_ingredient.append(item["original"])

            set_ingredient["ingredients"] = list_ingredient
            set_ingredient["instructions"] = data['instructions']

            return Response(set_ingredient)
        except :
            return Response(
                { "Error":"Something wrong" },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )