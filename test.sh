#!/usr/bin/env bash

URL=http://localhost:8001/

echo -e "\nTest if working, should return I'm listening"
curl ${URL}

echo -e "\nAdd new document, returns cluster 0"
curl ${URL}add -H "Content-Type: application/json" -X POST -d '{
	"document": {
		"id": 1,
		"text": "Russia"
	}
}'

echo -e "\nIf only one similar cluster exists, will return that cluster id, 0 in this case"
curl ${URL}add -H "Content-Type: application/json" -X POST -d '{
	"document": {
		"id": 11,
		"text": "Russia"
	}
}'

echo -e "\nAdd different document, returns cluster 1"
curl ${URL}add -H "Content-Type: application/json" -X POST -d '{
	"document": {
		"id": 2,
		"text": "Obama"
	}
}'


echo -e "\nWill create new cluster 2, merging clusters 0 and 1"
curl ${URL}add -H "Content-Type: application/json" -X POST -d '{
	"document": {
		"id": 3,
		"text": "Obama in Russia"
	}
}'

echo -e "\nThe same thing again will return cluster 2, because ID exists"
curl ${URL}add -H "Content-Type: application/json" -X POST -d '{
	"document": {
		"id": 1,
		"text": "Russia"
	}
}'

echo -e "\nThe same thing from previous cluster 0 will return cluster 2 because of merge"
curl ${URL}add -H "Content-Type: application/json" -X POST -d '{
	"document": {
		"id": 5,
		"text": "Russia"
	}
}'

echo -e "\nClear the database"
curl ${URL}clear

echo -e "\nNow the same thing will return 0"
curl ${URL}add -H "Content-Type: application/json" -X POST -d '{
	"document": {
		"id": 1,
		"text": "Russia"
	}
}'

echo -e "\n"