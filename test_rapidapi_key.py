import http.client

conn = http.client.HTTPSConnection("upwork-jobs-api2.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "484377fa76mshc9a5b3875e2f583p15804bjsn5cbe55889a7e",
    'x-rapidapi-host': "upwork-jobs-api2.p.rapidapi.com"
}

conn.request("GET", "/active-freelance-1h?limit=10", headers=headers)

res = conn.getresponse()
print(f"Status: {res.status} {res.reason}")
data = res.read()
print("Response:")
print(data.decode("utf-8")) 