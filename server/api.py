import json
import logging
from fastapi import FastAPI, Request, Response
from logging.handlers import TimedRotatingFileHandler


app = FastAPI()


logging.basicConfig(level=logging.DEBUG)
handler = TimedRotatingFileHandler(
    filename='requests.log', when='midnight', backupCount=7
)
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s'
    )
)
logging.getLogger().addHandler(handler)


@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(
        f"{request.method} {request.url.path} from {request.client.host}"
    )

    if request.headers:
        logging.debug(f"Headers: {dict(request.headers)}")

    if request.method in ['POST', 'PUT', 'PATCH']:
        body = await request.body()
        logging.debug(f"Request Body: {body.decode('utf-8')}")

    if request.query_params:
        logging.debug(f"Query Parameters: {request.query_params}")

    return await call_next(request)


@app.get("/_logs")
async def get_logs():
    with open("requests.log", "r") as f:
        logs = f.read()

    return Response(content=logs, media_type="text/plain")


@ app.get("/{path:path}")
async def handle_get_request(request: Request, path: str):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print("============== New GET Request ==============")

    print("------------------ Headers ------------------")
    print(json.dumps(dict(request.headers), indent=4))
    print("----------------------------------------------")

    print("---------------- Query Params ---------------")
    print(json.dumps(request.query_params._dict, indent=4))
    print("----------------------------------------------")

    print("==============================================")

    if mode and token:
        if mode == "subscribe" and token == "TOKEN":
            print("WEBHOOK_VERIFIED")

            return Response(content=challenge)
        else:
            print("Responding with 403 Forbidden")

            return {"message": "Forbidden"}
    else:
        return {"message": "success"}


@ app.post("/{path:path}")
async def handle_post_request(request: Request, path: str):
    print("============== New POST Request ==============")

    print("------------------ Headers -------------------")
    print(json.dumps(dict(request.headers), indent=4))
    print("----------------------------------------------")

    print("------------------- Body ---------------------")
    bd = await request.body()
    bd = json.loads(bd.decode("utf-8"))
    print(json.dumps(bd, indent=4))
    print("----------------------------------------------")

    print("==============================================")

    return {"message": "success"}
