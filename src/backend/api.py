from fastapi import FastAPI
import sentry_sdk

from dotenv import load_dotenv
load_dotenv()


import os


SENTRY_DSN = os.getenv("SENTRY_DSN")
print(SENTRY_DSN)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

app = FastAPI()

@app.get('/sentry-debug')
async def trigger_error():
    error_source = 1 / 0