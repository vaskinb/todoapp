# TODO APP

### Вимоги

1. Наявність python >= 3.11.0
2. Наявність віртуального середовища

### Опис файлів
<details><summary>Файли</summary>

* `app` - основний каталог роботи с додатком
* * `app/auth/` - директорія з файлами для авторизації, автентифікації та 
    реєстрації користувачів
* * `app/main/` - директорія з файлами представлень додатку
* * `app/static/` - директорія зі статичними файлами
* * `app/templates/` - директорія з HTML-шаблонами для відображення
* * `app/utils/` - директорія з утилітами
* * `app/app.py` - основний файл для створення та налаштування Flask-додатку
* * `app/models.py` - моделі бази даних
* `.gitignore` - файл с налаштуваннями для GIT
* `config.py` - файл з базовими налаштуваннями конфігурації додатку
* `manage.py` - файл для керування додатком та виконання команд
* `README.md` - файл з описом проєкту, інструкцією з налаштування та 
використання
* `requirements.txt` - файл з бібліотеками для встановлення
* `run.sh` - файл для запуску допоміжних сервісів та тестів
* `wsgi.ini` - конфігураційний файл для запуску додатку через uWSGI 
* `wsgi.py` - точка входу для запуску додатку через wsgi
</details>

### Опис функціоналу

<details><summary>Опис</summary>

Програма являє собою комплексний інструмент для керування задачами, який 
складається з 3-х основних модулів:

#### 1. Dashboard

**Основні можливості:**

- **Створення задач:**  
  Користувач може створити нову задачу, заповнивши форму (TaskForm). 
При створенні задачі вказується заголовок, опис, дата виконання (due_date) та
початковий статус (за замовчуванням — _pending_).

- **Відображення задач:**  
  Задачі користувача відображаються у вигляді таблиці з наступними категоріями:
  - **All:** відображаються всі задачі.
  - **Pending:** задачі, що ще не почали виконуватись.
  - **Active:** задачі, над якими ведеться робота.
  - **Completed:** задачі, що були виконані.

- **Редагування та зміна статусів:**  
  Для кожної задачі доступні дії: 
редагування, видалення, зміна статусу (через кнопки "Start", "Done", "Undo"). 
Це дозволяє швидко коригувати інформацію про задачу або перемикати її стан.

- **RESTful API:**  
  Реалізовані маршрути для:
- ***створення (`/tasks/add`)***, 
- ***отримання (`/tasks/get/<task_id>`)***, 
- ***редагування (`/tasks/edit/<task_id>`)***, 
- ***видалення (`/tasks/delete/<task_id>`)***, 
- ***зміни статусу задачі (`/tasks/set_status/<task_id>`)***.

#### 2. Calendar

**Основні можливості:**

- **Інтеграція з FullCalendar:**  
  Модуль календаря використовує FullCalendar для візуалізації задач,
що дозволяє користувачу бачити задачі, розташовані за датами.

- **Drag & Drop:**  
  Реалізовано можливість перетягувати задачі між датами безпосередньо в
календарі, що спрощує планування і зміну дат виконання.

- **Створення та редагування:**  
  За допомогою календарного інтерфейсу користувач може створювати нові задачі 
або редагувати існуючі, використовуючи форму.

- **Зміна статусів:**  
  Користувач може змінювати статус задачі прямо в календарі.

#### 3. Statistic

**Основні можливості:**

- **Агрегація статистики:**  
  Модуль збирає та агрегує дані по задачах користувача. 
Формуються такі основні показники:
  - Загальна кількість задач.
  - Кількість задач у статусах `pending`, `active` та `completed`.

- **Динамічні графіки:**  
  Побудова двох типів графіків:
  - **Щоденна статистика:**  
    Графік, що відображає дані за останні 7 днів, де для кожного дня вказується
загальна кількість задач та кількість виконаних.
  - **Щотижнева статистика:**  
    Графік, що відображає дані за останні 4 тижні, де для кожного тижня 
відображаються загальна кількість задач та кількість виконаних.

</details>

### Встановлення

<details><summary>Процеc встановлення</summary>

#### Оновлення
* Оновлення сервера

``` shell
apt update && apt upgrade -y
```


#### PostgreSQL
* Встановлення PostgreSQL
```shell
apt install postgresql postgresql-contrib
```

* Створення БД PostgreSQL
```
$ sudo -u postgres psql
postgres=# create database limitless;
postgres=# create user todoapp with encrypted password 'todoapp';
postgres=# grant all privileges on database todoapp to todoapp;
```

* Створення тестової БД PostgreSQL (для локального тестування)
```
$ sudo -u postgres psql
postgres=# create database todoapp_test;
postgres=# create user todoapp_test with encrypted password 'todoapp_test';
postgres=# grant all privileges on database todoapp_test to todoapp_test;
```

* Створення міграцій БД
```
$ ./run.sh db init
$ ./run.sh db migrate
$ ./run.sh db upgrade
```


#### Supervisor
* Встановлення supervisor

``` shell
apt install supervisor
```

* Налаштування supervisor
```txt
[program:app]
command=/root/todoapp/venv/bin/uwsgi --ini /root/todoapp/wsgi_admin.ini --chdir /root/todoapp
autostart=true
autorestart=true
stopasgroup=true
stopsignal=QUIT
stderr_logfile=/var/log/%(program_name)s.log
stdout_logfile=/var/log/%(program_name)s.log
```

#### Project
* Встановлення git та отримання проєкту

``` shell
git clone git@github.com:vaskinb/todoapp.git
```

* Встановлення віртуального середовища

``` shell
apt install virtualenv
virtualenv -p python3 venv
. venv/bin/activate
```

* Встановлення залежностей

``` shell
pip install -r requirements.txt
```
</details>
