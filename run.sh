set +e
echo "==> Run FastApi-Todos App with docker"
docker run -d --name todo_app -p 80:80 todo_app