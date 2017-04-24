calcdjt
============================

Tweet Reference information
Tweet Object field guide:  https://dev.twitter.com/overview/api/tweets

Create `config.json`
```json
{
  "CONSUMER_KEY":"twitter consumer key",
  "CONSUMER_SECRET":"twitter consumer secret",
  "ACCESS_KEY":"twitter access key", 
  "ACCESS_SECRET":"twitter access secret",
  "MONGO_URI":"MongoDB Connection String"
}
```
###Docker Build Command
```
docker build --rm=true -t djt .
```