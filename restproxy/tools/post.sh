#!/bin/sh

curl -v -X POST -H "Content-Type: application/json" -d @in.json http://127.0.0.1:8080/public_fourth
