import time
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
import numpy as np
import requests
import threading
import os
import logging

from .generate_surface import generate_demo_surface
from .render_surface import render_surface_html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRICER_AVAILABLE = False
PRICER_HEALTH_URL = os.environ.get("PRICER_HEALTH_URL", "http://pricer:8080/healthz")
CPPRICER_URL = os.environ.get("CPPRICER_URL", "http://pricer:8080/price")


app = FastAPI()

def check_pricer_health():
    global PRICER_AVAILABLE
    try:
        resp = requests.get(PRICER_HEALTH_URL, timeout=0.5)
        PRICER_AVAILABLE = resp.status_code == 200
    except Exception:
        PRICER_AVAILABLE = False

@app.on_event("startup")
def startup_event():
    def background_probe():
        while True:
            check_pricer_health()
            time.sleep(5)
    threading.Thread(target=background_probe, daemon=True).start()

@app.get("/surface")
def surface():
    return generate_demo_surface()

@app.get("/status")
def status():
    """Return current pricing source status for UI."""
    source = "cpp" if check_cpp_available() else "local"
    return {
        "pricer_available": source == "cpp",
        "active_source": source
    }


def check_cpp_available() -> bool:
    try:
        resp = requests.get(PRICER_HEALTH_URL, timeout=0.2)
        return resp.status_code == 200
    except:
        return False

@app.get("/price")
def price(
    strike: float = Query(...),
    expiry: float = Query(...),
    spot: float = Query(1.0),     # default spot
    rate: float = Query(0.05),    # default interest rate
    vol: float = Query(0.2)       # default vol
):
    """Return price for given strike/expiry and source info"""
    logger.info(f"Incoming price request: strike={strike}, expiry={expiry}")
    if check_cpp_available():
        try:
            logger.info(f"Attempting C++ pricer at {CPPRICER_URL}")
            resp = requests.get(
                CPPRICER_URL,
                params = {
                    "strike": strike,
                    "expiry": expiry,
                    "spot": spot,
                    "rate": rate,
                    "vol": vol,
                },
                timeout=0.5
            )
            resp.raise_for_status()
            cpp_data = resp.json()
            logger.info(f"C++ returned {cpp_data}")

            # Pick call or put if available, even if 0.0
            call_price = cpp_data.get("call")
            put_price = cpp_data.get("put")

            price = call_price if call_price is not None else put_price

            if price is not None:
                return {
                    "strike": strike,
                    "expiry": expiry,
                    "price": price,
                    "source": "cpp"
                }
        except requests.RequestException as e:
            # silently fallback to local if C++ pricer fails
            logger.warning(f"C++ pricer failed: {e}")
            pass

    # Local fallback pricing
    local_price = strike * np.exp(-0.05 * expiry)

    return {
        "strike": strike,
        "expiry": expiry,
        "price": local_price,
        "source": "local"
    }

@app.get("/", response_class=HTMLResponse)
def index():
    return render_surface_html()

def generate_demo_surface():
    strikes = np.linspace(0.5, 1.5, 30)   # strike ratio (K/S)
    tenors = np.linspace(0.1, 2.0, 25)    # in years

    surface = []
    for t in tenors:
        row = []
        # long-dated options are flatter, short-dated are more smiley
        for k in strikes:
            base_vol = 0.2
            smile = 0.25 * np.exp(-t) * (k - 1)**2   # curvature diminishes with tenor
            term_structure = 0.02 * np.sqrt(t)       # vol slightly increases with tenor
            vol = base_vol + smile + term_structure
            row.append(float(vol))
        surface.append(row)
    return {
        "strikes": strikes.tolist(),
        "tenors": tenors.tolist(),
        "vols": surface
    }
