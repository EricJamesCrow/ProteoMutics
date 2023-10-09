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

/home/cam/Documents/repos/ProteoMutics/backend/test/test_data/UV.vcf
/home/cam/Documents/repos/ProteoMutics/backend/test/test_data/dyads.bed
/home/cam/Documents/repos/ProteoMutics/backend/test/test_data/hg19.fa
/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/nucleosome/hg19_MNase_nucleosome_map_all.bed
/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/lesion_files/proteomutics/vcf/SRR_64-65-66_subset.vcf
/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/lesion_files/proteomutics/vcf/SRR_64-65-66.vcf
/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/lesion_files/proteomutics/vcf/SRR_67-68.vcf
/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/lesion_files/proteomutics/vcf/SRR_69-70.vcf
/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/HMCES_KBr.vcf
/media/cam/Working/8-oxodG/8-oxodG_Final_Analysis/vcf_files/genotype_split/WT_KBr.vcf