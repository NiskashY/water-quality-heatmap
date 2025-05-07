
# Для того чтобы установить зависимости
npm install 
# Для того чтоб запустить сервер ?? (можно просто открывать index.html но в отключенном браузере) 
npm run start

# для запуска сервера по обработке входящих запросов
flask --app endpoints/hex_endpoints run

# В браузер заходим через 
$ google-chrome  --disable-web-security --user-data-dir=tmp_for-disabled-web-security/
