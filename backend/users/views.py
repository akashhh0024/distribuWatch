from rest_framework.response import Response
from rest_framework.views import APIView


from .tokens import create_access_token, create_refresh_token
from .models import User


from .serializers import RegisterSerializer

# Create your views here.


class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "id":user.id,
                    "email":user.email
                },
                status=201,
            )

        return Response(serializer.errors, status=400)


class LoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {
                    "detail":"Invalid email or password"
                },
                status = 401,
            )
        
        if not user.check_password(password):
            return Response(
                {
                    "detail":"Invalid email or password"
                },
                status=401,
            )
        
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        return Response(
            {
                "access": access_token,
                "refresh": refresh_token,
            },

            status=200,
        )
