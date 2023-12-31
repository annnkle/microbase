# microbase

## Requirements

1. Python 3.9 or higher
2. R ~ 4
3. Pandoc

## Setup

1. Create python virtual environment and activate it

   `python -m venv venv && source venv/bin/activate` (on Linux)

   **(Run all python commands with virtual env activated.)**

2. Install python dependencies

   `pip install -r requirements.txt`

3. Create R virtual environment

   `Rscript setup_r_env.R`

4. Create `.env` file from `.env.template`

   `cp .env.template .env`

5. Generate `SECRET_KEY` and put it in `.env` file

   `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

6. Provide configuration for your database in the `settings.py` file (or leave as it is for default, lightweight `sqlite` db)

   - `MySQL` and `MariaDB`:

     - Install the `mysqlclient` package

       `pip install mysqlclient`

     - example configuration in `settings.py`:

       ```{python}
       'microbase': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'your_db_name',
             'USER': 'your_user',
             'PASSWORD': 'your_password',
             'HOST': 'localhost',
             'PORT': '3306'
       },
       ```

   - `PostgreSQL`:

     - Install the `psycopg2` package

       `pip install psycopg2`

     - example configuration in `settings.py`:

       ```{python}
       'microbase': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432'
       },
       ```

   - For more information refer: [Django db configuration documentation](https://docs.djangoproject.com/en/4.1/ref/databases/)

7. Apply database migrations

   `python manage.py migrate`

8. Create admin user

   `python manage.py createsuperuser`

9. Collect static files

   `python manage.py collectstatic`

## Running

Run the project with python virtual env activated:

`python manage.py runserver`
