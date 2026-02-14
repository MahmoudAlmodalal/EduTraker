from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CaseInsensitiveEmailBackend(ModelBackend):
    """
    Custom authentication backend that performs case-insensitive email lookup.
    This ensures users can login with any case variation of their email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user with case-insensitive email matching.
        
        Args:
            request: The HTTP request object
            username: The email address (named 'username' for compatibility with Django)
            password: The user's password
            **kwargs: Additional keyword arguments
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None
        
        try:
            # Perform case-insensitive email lookup
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        
        # Check the password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
