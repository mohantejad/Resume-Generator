OAUTH_PROVIDERS = {
    "google": {
        "client_id": "YOUR_GOOGLE_CLIENT_ID",
        "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "redirect_uri": "http://localhost:8000/auth/google/callback",
    },
    "linkedin": {
        "client_id": "YOUR_LINKEDIN_CLIENT_ID",
        "client_secret": "YOUR_LINKEDIN_CLIENT_SECRET",
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "userinfo_url": "https://api.linkedin.com/v2/me",
        "email_url": "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
        "redirect_uri": "http://localhost:8000/auth/linkedin/callback",
    },
}
