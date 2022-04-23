import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        "server.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="/etc/letsencrypt/live/fergl.ie/privkey.pem",
        ssl_certfile="/etc/letsencrypt/live/fergl.ie/fullchain.pem"
    )
