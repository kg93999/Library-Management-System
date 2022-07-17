# Library-Management-System

---

To get the project running do:

- Clone this repo
    ```shell
    $ git clone https://github.com/kg93999/Library-Management-System.git
    ```
- Open newly created directory `Library-Management-System` 
    ```shell
    $ cd Library-Management-System
    ``` 
- Create and activate virtual environment.
   ```shell
   python -m venv venv
   ```
   ```shell
   source venv/bin/activate
   ```
- Install requirements
    ```shell
    (.venv) $ pip install -r requirements.txt
    ```
- Run the following commands
    ```shell
    python manage.py makemigrations
    ```
    ```shell
    python manage.py migrate
    ```
    ```shell
    python manage.py runserver
    ```
