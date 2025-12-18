# Google Custom Search API Setup (100 Free Searches/Day)

## Step 1: Get Google API Key (2 minutes)

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"API Key"**
3. Copy your API key (looks like: `AIzaSyD...`)
4. Click **"Restrict Key"** (optional but recommended)
   - Under "API restrictions" → Select "Custom Search API"

## Step 2: Create Search Engine ID (2 minutes)

1. Go to: https://programmablesearchengine.google.com/
2. Click **"Add"** or **"Get Started"**
3. Enter:
   - **Sites to search:** `*` (asterisk = search entire web)
   - **Name:** MetaPersona Search
4. Click **"Create"**
5. Copy your **Search Engine ID** (looks like: `a1b2c3d4e5f...`)

## Step 3: Add to Your .env File

Open `MetaPersona-\.env` and add these lines:

```env
# Google Custom Search API (100 free queries/day)
GOOGLE_API_KEY=your_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
SEARCH_PROVIDER=google
```

## That's it!

Now when you run `python metapersona.py chat`, searches will use Google (fast and reliable).

### Free Tier Limits:
- ✅ **100 searches per day** (free)
- ✅ Instant results (< 1 second)
- ✅ High quality Google results

### Fallback:
If you hit the daily limit or don't set up Google, it automatically falls back to SearXNG (slower but unlimited).

---

**Test it:**
```bash
python metapersona.py chat
# Ask: "What are the latest bowling ball releases from Storm?"
```
