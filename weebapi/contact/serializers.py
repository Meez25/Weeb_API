from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name',
                  'phone_number', 'email_address', 'message']
