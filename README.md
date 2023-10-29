# ProteoMutics (In-Development)
a bioinformatics program that plots patterns between mutations and nucleosomes

### START FRONTEND ###

```
cd ./frontend
npm install
npm run start
```

### INSTALL AND START BACKEND WITHOUT DOCKER ###
```
cd ./backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-include "*"
```
### START BACKEND ###
```
cd ./backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-include "*"
```
### CREATE AND START DOCKER ENVIRONMENT (DEVELOPMENT) ###
```
docker-compose up -d --build
```
### START DOCKER ENVIRONMENT (DEVELOPMENT) ###
```
docker-compose up -d proteomutics-api
```
### EXECUTE COMMANDS IN DOCKER ENVIRONMENT (DEVELOPMENT) ###
```
docker-compose exec app bash
```
### CREATE AND START BACKEND WITH DOCKER (PRODUCTION) ###
```
docker build -t proteomutics-api .
docker run -d -p 8000:8000 proteomutics-api
```

/media/cam/Working/ProteoMuticsTest/WT_KBr.vcf
/media/cam/Working/ProteoMuticsTest/hg19_MNase_nucleosome_map_all_subset.bed
/media/cam/Working/ProteoMuticsTest/hg19.fa
/media/cam/Working/ProteoMuticsTest/hg19_MNase_nucleosome_map_all.bed
/media/cam/Working/ProteoMuticsTest/hg19_MNase_nucleosome_map_intergenic.bed