# Сайт
https://testniskashywaterqualityheatmaprepo.ip-ddns.com/

# Заходим в виртуальное окружение питона

```
# Без этого пункта установка зависимостей может быть сложнее (как минимум на MacOS нельзя устанавливать пакеты system-wide)
$ source ./bin/activate
```

# Установка зависимостей

```
# Устанавливаем зависимости для фронта
$ npm install
# Устанавливаем зависимости сервера
$ pip install -r ./requirements.txt
```

# Запуск

```
# Запускаем фронт. Запускается на localhost:8080
$ npm run start
# Запускаем бек. Запускается на 127.0.0.1:5050 (тоже локалхост)
$ flask --app endpoints/hex_endpoints run
```

