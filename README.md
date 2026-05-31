# food_exp

For Development (right now)
Everyone runs the backend locally on their own machine. Each person puts their own IP in api.js. Not ideal but fine for now.

For Others to Actually Use the App
You need to deploy the backend to a server. Cheapest and fastest option: Railway.
Step 1: Deploy backend to Railway

Go to railway.app
Sign up with GitHub
New Project → Deploy from GitHub repo → select food_exp
Set root directory to backend
It auto-detects FastAPI and deploys it
Railway gives you a public URL like https://food-exp-backend.railway.app

Step 2: Update api.js
javascriptconst BASE_URL = 'https://food-exp-backend.railway.app';
Now everyone uses that URL — no IP needed.
Step 3: Share the app
For others to run the mobile app without building it, use Expo Go + EAS:
powershellnpm install -g eas-cli
eas login
eas update
This gives you a shareable link anyone with Expo Go can open.