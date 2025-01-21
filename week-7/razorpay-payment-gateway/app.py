import razorpay
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

load_dotenv(".env")
RZR_ID = os.getenv("RZR_ID")
RZR_SECRET = os.getenv("RZR_SECRET")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse('static/new_order.html')

@app.get("/success")
async def success():
    return FileResponse('static/success.html')

@app.get("/config")
async def get_config():
    return {"key": RZR_ID}

@app.post("/create_order")
async def create_order():
    order_data = {'amount': 10000, 'currency':'INR'}
    client = razorpay.Client(auth=(RZR_ID, RZR_SECRET))
    payment = client.order.create(data=order_data)
    return {"order_id": payment['id'], "amount": payment['amount']}