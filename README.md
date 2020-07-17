gustos
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
  "MONGO_URI":"MongoDB Connection String",
  "TWITTER_TARGETS":[
   "List of Twitter IDs to capture"
  ],
  "RESPONSE_TARGETS":[
    "List of Twitter IDs to target & respond to"
  ]
}
```

### Docker Build Command

```
docker build --rm=true -t gustos .
```

### Docker Run -d 

```
docker run -d --restart unless-stopped --name app-gustos gustos:latest
```
