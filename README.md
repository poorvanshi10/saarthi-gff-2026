# Saarthi Backend (SBI GFF 2026)

This is the core backend API for Saarthi. We built this to fix the massive drop-off rates in digital KYC pipelines (which are currently sitting around 60%). 

Instead of a standard CRUD app that just throws a "400 Bad Request" when a user's PAN card upload fails, this backend acts as a state-aware agent. It intercepts the failure, scores the lead, and dynamically routes them to a conversational recovery loop.

Note: This repo is purely the headless API. 

## How it works under the hood

1. **Lead Scoring (XGBoost):** Every session is piped through a local XGBoost model. If a user drops off, the model scores their conversion probability so we know if they are worth spending compute/human resources to recover.
2. **State Machine:** The FastAPI router doesn't just return static responses. It tracks exactly where the user is in the onboarding graph. 
3. **Cross-Channel Memory:** We use MongoDB to persist session state. If a user rage-quits the web portal, the state is saved so the session can be recovered via WhatsApp later without making them start over.

## Tech Stack

* **API:** Python 3.10, FastAPI, Uvicorn
* **ML:** XGBoost, Scikit-learn, Pandas
* **Database:** MongoDB

## Running it locally

If you are a judge evaluating this repo, here is the fastest way to spin it up:

```bash
# 1. Clone it
git clone [https://github.com/poorvanshi10/saarthi-gff-2026.git](https://github.com/poorvanshi10/saarthi-gff-2026.git)
cd saarthi-gff-2026

# 2. Setup your virtual env so you don't mess up your global packages
python -m venv .venv
.venv\Scripts\activate  # (Use `source .venv/bin/activate` if on Mac/Linux)

# 3. Install requirements
pip install -r requirements.txt

# 4. Run the server
uvicorn main:app --reload
