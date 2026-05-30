from flask import Flask, request
import os

app = Flask(name)

@app.route("/", methods=["GET", "POST"])
def webhook():

if request.method == "GET":
    return "Bot Running"

print("POST RECEIVED")
print(request.get_json())

return "OK"

if name == "main":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 10000))
)
