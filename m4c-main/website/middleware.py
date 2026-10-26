class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Email and WhatsApp verification are optional for M4C members.
        # Members may access the account and profile pages immediately.
        return self.get_response(request)
