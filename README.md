# ProteoMutics
a bioinformatics program that plots patterns between mutations and nucleosomes

### START FRONTEND ###

```
cd ./frontend
npm install
npm run start
```
### START BACKEND WITH DOCKER (DEVELOPMENT) ###
```
docker-compose up --build
```
### START BACKEND WITH DOCKER (PRODUCTION) ###
```
docker build -t proteomutics-api .
docker run -d -p 8000:8000 proteomutics-api
```
### START BACKEND WITHOUT DOCKER ###
```
cd ./backend
pip3 install -r requirements.txt
python3 manage.py runserver
```
