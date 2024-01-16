![Pasted image](https://github.com/annnkle/microbase/assets/95099151/c9c10abd-e044-4ab1-9369-f366b69b387b)

Microbase is a tool/platform dedicated for everyone who wants to keep their microbial research data neatly organized and ready to use. It stores taxonomic data tables but perhaps most importatnly it accustomes to any metadata categories the user specifies beforehand. Here is how database configuration goes:

![image](https://github.com/annnkle/microbase/assets/95099151/866e4c54-fb9d-495a-81c9-213e21aea89d)

This page shows on the first-time run.

The entered categories are later used for building queries and filtering.

![search1](https://github.com/annnkle/microbase/assets/95099151/c8f59374-d3f3-400e-9b9b-adeb125e68f9)

The resulting datasets can be readily downloaded as csv files...

![image](https://github.com/annnkle/microbase/assets/95099151/3050c765-4041-40e7-b015-887f60d6ab34)

...used to create stacked bar plots and heatmaps (ggplot2 + plotly powered) or serve as a basis for PCA or alpha/beta diversity analysis.

![image](https://github.com/annnkle/microbase/assets/95099151/608364fe-b810-4888-9509-149671e8ea7c)

All records in the database can be browsed on a specific page, without entering a query.

![browse](https://github.com/annnkle/microbase/assets/95099151/001b12ac-3205-43ae-b90f-077445bdecb3)

Records can be uploaded one-by-one or in batches. In the former case, the upload form conveiniently adjusts to the categories configured in the setup.

![upload](https://github.com/annnkle/microbase/assets/95099151/5cab416a-cb4b-43c6-9b9b-23be39c3d527)


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
