# Social Media MCP Setup Guide

## Overview

The Twitter, Facebook, and Instagram MCPs use **persistent browser sessions** (same architecture as WhatsApp). This means you only need to log in once, and the session will be saved for future use.

## Architecture

Each social media MCP uses Playwright's `launch_persistent_context` with a dedicated session directory:

- **Twitter**: `~/.twitter_session/`
- **Facebook**: `~/.facebook_session/`
- **Instagram**: `~/.instagram_session/`

These directories store the full browser profile (cookies, localStorage, IndexedDB), so you stay logged in between MCP calls.

## Initial Setup

### Step 1: Verify Credentials

Make sure your `.env` file has the correct credentials:

```bash
# Twitter
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password

# Facebook
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password

# Instagram
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### Step 2: Initialize Sessions

Run the initialization script to log in once and save the session:

```bash
# Initialize all platforms at once
cd My_AI_Employee
python scripts/setup/initialize_social_sessions.py all

# Or initialize one platform at a time
python scripts/setup/initialize_social_sessions.py twitter
python scripts/setup/initialize_social_sessions.py facebook
python scripts/setup/initialize_social_sessions.py instagram
```

**What happens:**
1. A browser window will open for each platform
2. You'll be taken to the login page
3. Log in manually (the script will detect when you're logged in)
4. Press Ctrl+C when you see the home feed
5. The session is saved automatically

### Step 3: Verify Health

Test that the MCPs can use the saved sessions:

```bash
# Test Twitter
ccr mcp call twitter-web-mcp health_check

# Test Facebook
ccr mcp call facebook-web-mcp health_check

# Test Instagram
ccr mcp call instagram-web-mcp health_check
```

Expected output:
```json
{
  "status": "healthy",
  "logged_in": true,
  "message": "Twitter session is active",
  "timestamp": "2026-02-04T18:00:00.000Z"
}
```

## Troubleshooting

### "Session expired" error

If you see `"logged_in": false` or `"session expired"`, the session needs to be re-initialized:

```bash
python scripts/setup/initialize_social_sessions.py twitter
```

### Browser doesn't open on WSL

If you're on WSL and the browser doesn't open:

1. Make sure you have X11 forwarding set up, OR
2. Run the script from Windows PowerShell instead:

```powershell
cd D:\hackathon-0\My_AI_Employee
python scripts\setup\initialize_social_sessions.py twitter
```

### "Could not detect successful login"

This warning appears if the script couldn't verify you logged in. Check manually:

1. Look at the browser window - are you on the home feed?
2. If yes, the session is saved (ignore the warning)
3. If no, try logging in again

### Session directories

If you need to reset a session (e.g., to use a different account):

```bash
# Delete the session directory
rm -rf ~/.twitter_session
rm -rf ~/.facebook_session
rm -rf ~/.instagram_session

# Then re-initialize
python scripts/setup/initialize_social_sessions.py all
```

## How It Works

### Persistent Context Architecture

The MCPs use Playwright's `launch_persistent_context` which:

1. **Saves everything**: Cookies, localStorage, IndexedDB, Service Workers
2. **Survives restarts**: Session persists even if the MCP server restarts
3. **No re-authentication**: Once logged in, you stay logged in
4. **Same as WhatsApp**: Uses the exact same architecture as your working WhatsApp MCP

### Example: Twitter MCP

```python
# From twitter_web_mcp.py
self.context = await self.playwright.chromium.launch_persistent_context(
    user_data_dir=str(self.session_dir),  # ~/.twitter_session
    headless=False,
    args=['--disable-blink-features=AutomationControlled'],
    viewport={'width': 1280, 'height': 720},
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    locale='en-US',
    timezone_id='America/New_York'
)
```

### Session Lifecycle

1. **First run**: Session directory is empty → MCP tries to log in using credentials
2. **Subsequent runs**: Session directory has saved state → MCP uses existing session
3. **Session expires**: MCP detects expired session → tries to re-authenticate
4. **Manual reset**: Delete session directory → start fresh

## Testing

### Test Twitter Posting

```bash
ccr mcp call twitter-web-mcp post_tweet \
  --text "Testing my AI Employee! 🤖" \
  --entry_id "test_001"
```

### Test Facebook Posting

```bash
ccr mcp call facebook-web-mcp post_to_facebook \
  --message "Hello from my AI Employee!" \
  --entry_id "test_002"
```

### Test Instagram Posting

```bash
ccr mcp call instagram-web-mcp post_to_instagram \
  --caption "AI Employee in action! 🚀" \
  --image_path "/path/to/image.jpg" \
  --entry_id "test_003"
```

## Next Steps

Once all three MCPs show `"status": "healthy"`, you're ready to:

1. ✅ Process action items from `/Needs_Action/`
2. ✅ Use the `/social-media-poster` skill
3. ✅ Run the complete Gold tier workflow
4. ✅ Test the orchestrator with social media tasks

## Related Files

- **MCPs**: `mcp_servers/twitter_web_mcp.py`, `facebook_web_mcp.py`, `instagram_web_mcp.py`
- **WhatsApp MCP** (reference): `mcp_servers/browser_mcp.py`
- **Initialization script**: `scripts/setup/initialize_social_sessions.py`
- **Environment**: `.env` (credentials)
