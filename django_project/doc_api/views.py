from django.shortcuts import render
from django.contrib.auth.models import User, Group
from . form import sentiment_form
from django.core import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from . serializers import UserSerializer, GroupSerializer, sentiment_Serializers
from . models import sentiment
import numpy as np


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class SentimentsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset =sentiment.objects.all()
    serializer_class = sentiment_Serializers