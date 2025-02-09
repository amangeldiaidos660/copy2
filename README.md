# Развертывание FastAPI и Flask на VPS

## 1. Подключение к серверу по SSH
```bash
ssh ubuntu@194.32.140.147
```
Если требуется root-доступ:
```bash
sudo -i
```

## 2. Установка необходимых пакетов
```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip git ufw
```

## 3. Настройка Firewall
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp  # Для Flask
ufw enable
```

## 4. Клонирование проектов из Git
```bash
mkdir -p /opt/projects && cd /opt/projects

git clone https://github.com/your-repo/fastapi_project.git

git clone https://github.com/your-repo/flask_project.git
```

## 5. Развертывание FastAPI
```bash
cd /opt/projects/fastapi_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4 --daemon
```
Проверка работы:
```bash
ss -tulnp | grep 8000
```

## 6. Настройка Nginx для FastAPI
```bash
apt install -y nginx
nano /etc/nginx/sites-available/fastapi
```
Добавить:
```nginx
server {
    listen 80;
    server_name alashcloud.kz;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Сохранить и активировать конфиг:
```bash
ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## 7. Установка SSL (Let's Encrypt)
```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d alashcloud.kz
```

## 8. Развертывание Flask
```bash
cd /opt/projects/flask_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```
Запуск Flask:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app --daemon
```
Проверка работы:
```bash
ss -tulnp | grep 5000
```
Теперь Flask доступен по IP сервера и порту `5000`.

## Готово! 🎉
FastAPI работает через Nginx на `alashcloud.kz`, а Flask — напрямую на порту `5000`. 🚀
