docker stop mir-misis
docker build  -t mir-misis-back -f  Dockerfile .
docker run -it -p 5000:8080 --rm --name mir-misis mir-misis-back  