from pathlib import Path
from dotenv import load_dotenv
import os
import boto3

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-%s^cc61v(u)=*_owba2+a@hnfnxa%a8vgnt26v!&0@21_*jz7w'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',  
    'social_django',  
    'users',
    'feed',
    'madlibs',
    'social',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


REST_FRAMEWORK = {
     'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Default: all endpoints require auth
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50
}

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

SESSION_ENGINE = 'core.sessions'
#SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session cookie settings for OAuth
SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cookies to be sent with OAuth redirects
SESSION_COOKIE_HTTPONLY = True   # Prevent JavaScript access to session cookie
SESSION_COOKIE_SECURE = False    # Set to True in production with HTTPS
SESSION_COOKIE_AGE = 1209600     # 2 weeks in seconds
SESSION_COOKIE_DOMAIN = None     # Allow cookies to work across localhost/127.0.0.1
SESSION_SAVE_EVERY_REQUEST = True  # Ensure session is saved on every request


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DB_USER = os.environ['MONGODB_CLIENT_USERNAME']
DB_PASSWORD = os.environ['MONGODB_CLIENT_PASSWORD']
MONGODB_NAME = os.environ['MONGODB_DB_NAME']
MONGODB_URI = f'mongodb+srv://{DB_USER}:{DB_PASSWORD}@{MONGODB_NAME}.2h0tvpx.mongodb.net/?retryWrites=true&ssl=true&w=majority&appName={MONGODB_NAME}'

#google OAuth2
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/auth/login/google-oauth2/'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'http://localhost:5173/'
LOGOUT_REDIRECT_URL = 'http://localhost:5173/'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',          
    'users.pipeline.create_mongodb_user',            
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]


SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'select_account',
    'access_type': 'offline',
}

SOCIAL_AUTH_GOOGLE_OAUTH2_USE_UNIQUE_USER_ID = True  # Use Google ID, not email
SOCIAL_AUTH_UNIQUE_USER_EMAIL = True  # Don't allow multiple accounts with same email
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'username']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {funcName}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core.settings': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'core.sessions': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'madlibs': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'madlibs.models': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'madlibs.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users.models': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

#AWS 
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
AWS_S3_URL = os.getenv("AWS_S3_URL")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

#Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMAGE_GENERATION_SYS_PROMPT = """You are an expert at creating coherent, visually appealing images from user-generated madlib stories. These stories may contain unusual, wacky, or seemingly nonsensical combinations of words and phrases.

Your task is to interpret the filled-in madlib text and generate an image that captures the essence of the scene, even when the content is absurd or surreal.

Guidelines:
1. Parse the narrative structure: Look beyond individual words to understand the overall scene, action, and context described in the madlib.

2. Create visual coherence: Even with bizarre combinations (like "a purple elephant dancing in a library with spaghetti"), compose a single unified scene that makes visual sense. Combine all elements naturally within one setting.

3. Use descriptive, photographic composition: Frame the scene with appropriate camera angles, lighting, and perspective. Think like a photographer or illustrator capturing this moment.

4. Balance realism with creativity: For realistic subjects, maintain natural proportions and lighting. For fantastical elements, ensure they're rendered with consistent style and detail.

5. Emphasize the main subject: Identify the primary focus of the madlib (usually the main noun/character) and make it the clear focal point of the image.

6. Fill in sensible defaults: If specific details are missing (time of day, background, colors), infer reasonable choices that complement the described elements.

7. Maintain a cohesive art style: Choose one consistent visual style (photorealistic, cartoon, illustration, etc.) appropriate to the content rather than mixing styles.

8. Handle contradictions gracefully: When elements conflict, prioritize the most important or first-mentioned element, and adjust others to create a harmonious scene.

9. To tell a story, create a comic strip with multiple panes of images

10. DO NOT ANY GENERATE ANY TEXT AT ALL!!!!

Remember: Your goal is to transform even the most unusual word combinations into a compelling, viewable image that brings the madlib story to life."""