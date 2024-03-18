FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# RUN python manage.py makemigrations
# RUN python manage.py migrate
# RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@admin.ru', 'admin')" | python manage.py shell

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]

# CMD python manage.py migrate \
#     && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='root').exists() or User.objects.create_superuser('root', 'root@example.com', 'root')" \
#     && python manage.py initialize_db \
#     && python manage.py collectstatic --no-input \
#     && gunicorn foodgram.wsgi: --bind 0.0.0.0:8000 