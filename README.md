# ChatBot Demo
An example that showcases the benefit of running AI inside Redis


This repository contains the backend web app built with Flask, front end built with Angular (compiled to native JS) and the model files required for the chatbot to work. Follow below steps to bring the chatbot up.

- Install `docker-compose` & `docker` if you don't have it
- Run `docker-compose up`. This will bring up the Flask application (application server for the chatbot) and redisai (database server and RedisAI with PyTorch runtime)

If you haven't seen any issues so far, you should have the flask application and RedisAI server up by now. Try out the API (we have only one API endpoint -> `/chat` which accepts `message` as the json key with your message as value) using `curl` like given below or access the simple UI at `http://localhost:5000`.

```
curl http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message": "I am crazy"}'
```

