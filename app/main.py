import uvicorn
import os
# import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status, Query
import httpx

load_dotenv()

app = FastAPI()

IPINFO_API_KEY = os.environ.get("IPINFO_API_KEY")
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")


async def get_location_from_ip(ip: str):
    url = f"https://ipinfo.io/{ip}?token={IPINFO_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Unable to fetch location data"
            )
        data = response.json()
        # print(json.dumps(data, indent=2))
        return {"city": data.get('city')}


async def get_temperature(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={
        city}&units=metric&appid={OPENWEATHERMAP_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Unable to fetch weather data"
            )
        data = response.json()
        # print(json.dumps(data, indent=2))
        return data["main"]["temp"]

# we are requesting:
# client_ip, location, temperature, city and
# greeting = "Hello, Mark!, the temperature is 11 degrees Celcius in New York"


@app.get("/", status_code=status.HTTP_200_OK)
async def get_info(request: Request, name: str = Query(..., description="your name")):
    client_ip = request.client.host
    location = await get_location_from_ip(client_ip)
    # print(json.dumps(location, indent=2))
    city = location.get("city")
    temperature = await get_temperature(city)
    greeting = f"Hello, {name}!, the temperature is {
        temperature} degrees Celcius in {city}"

    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": greeting
    }

    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
