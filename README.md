# Dynamic Data Web Scraper
## Simple repo containning a Dockerfile that creates a container able to run selenium in headless mode
### TEST
To start both the scraper and a PSQL instance
* docker-compose up  
Then enter the scrappy container
* docker exec -it my_scrappy /bin/bash  
Then run the scraper with
* python scrappy_script.py

### USE
* Clone repo
* change code in scrappy_script.py and config.json as needed
* Build Dockerfile
* repeat