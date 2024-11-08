from django.contrib.auth.models import User
from hb.models import FirstLevelUser

user = User.objects.get(id=18)
first_level_user = FirstLevelUser.objects.filter(user=user).first()
print(first_level_user)
