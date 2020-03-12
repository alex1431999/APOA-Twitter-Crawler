# Twitter Crawler

## Setup
Install python3:
```
$ sudo apt-get update
$ sudo apt-get install python3.6
```
Install venv:
```
sudo apt-get install python3-pip
sudo pip3 install virtualenv 
```
Create venv:
```
python3 -m venv venv
```
Insert `set_env.sh` in root directoy:
```
source ./venv/bin/activate
export PYTHON_ENV="<Env>" # DEVELOPMENT / PRODUCTION

# Mongo
export MONGO_CONNECTION_STRING="<connection-uri>"
export MONGO_DB_NAME="<db-name>"

# Celery
export BROKER_URL="<URL>"

# Secrets
export TWITTER_API_KEY="<Key>"
export TWITTER_API_KEY_SECRET="<Key-Secret>"

export TWITTER_ACCESS_TOKEN="<Token>"
export TWITTER_ACCESS_TOKEN_SECRET="<Token>"
```

## Testing
### Environment
````
export MONGO_URL='mongodb://localhost:27017'
export MONGO_DATABASE_NAME='test_twitter'
````

### Execution
````
python3 -m nose
````

## Development
Activate venv:
```
source set_env.sh
```
Run script:
```
python3 run.py <script-name>
```
### Available scripts
#### full
Runs all keywords which need a crawl result

#### streaming
Opens a stream for all keywords in the database

## Production
Activate venv:
```
source set_env.sh
```
Activate worker:
```
celery -A tasks worker -l info
```
