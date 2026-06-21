from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        # Exempt login page, django admin page, and static/media files
        if (
            path == '/' or 
            path.startswith('/admin/') or 
            path.startswith('/static/') or 
            path.startswith('/media/')
        ):
            return self.get_response(request)

        # Redirect unauthenticated users to the login page
        if not request.user.is_authenticated:
            return redirect('/')

        return self.get_response(request)
