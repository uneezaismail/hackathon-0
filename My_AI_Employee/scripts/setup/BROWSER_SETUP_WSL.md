# Browser Initialization on WSL - Solutions

## Problem

The browser automation scripts need to open a visible browser window for you to log in, but WSL doesn't have GUI support configured by default. The browser process starts but the window doesn't appear.

## Solution 1: Use Windows PowerShell (Recommended)

Since you're on WSL with a Windows mount (`/mnt/d/`), the easiest solution is to run the initialization script from Windows PowerShell instead.

### Steps:

1. **Open Windows PowerShell** (not WSL terminal)

2. **Navigate to your project:**
   ```powershell
   cd D:\hackathon-0\My_AI_Employee
   ```

3. **Run the initialization script:**
   ```powershell
   # Initialize Twitter
   .\scripts\setup\initialize_social_sessions.ps1 -Platform twitter

   # Or initialize all platforms
   .\scripts\setup\initialize_social_sessions.ps1 -Platform all
   ```

4. **What happens:**
   - Browser window opens on your Windows desktop
   - You log in manually
   - Press Ctrl+C when done
   - Session is saved to project directory (`.twitter_session/`, etc.)

5. **Verify from WSL:**
   ```bash
   cd /mnt/d/hackathon-0/My_AI_Employee
   ls -la .twitter_session/
   ```

## Solution 2: Enable WSLg (WSL GUI Support)

If you want to run GUI apps directly from WSL, you need WSLg (available in WSL 2).

### Check if you have WSLg:

```bash
echo $DISPLAY
# Should show something like :0 or :1
```

If empty, you need to:

1. **Update WSL to latest version:**
   ```powershell
   # In Windows PowerShell (as Administrator)
   wsl --update
   wsl --shutdown
   ```

2. **Restart WSL:**
   ```bash
   # In WSL terminal
   exit
   # Then open a new WSL terminal
   ```

3. **Verify WSLg is working:**
   ```bash
   # Test with a simple GUI app
   sudo apt install x11-apps -y
   xeyes
   # You should see a window with eyes following your cursor
   ```

4. **If WSLg works, run the initialization script:**
   ```bash
   cd /mnt/d/hackathon-0/My_AI_Employee
   uv run python scripts/setup/initialize_social_sessions.py twitter
   ```

## Solution 3: Manual Browser Login (Fallback)

If neither solution works, you can manually set up the sessions:

1. **Start the MCP server directly:**
   ```bash
   cd /mnt/d/hackathon-0/My_AI_Employee
   uv run python mcp_servers/twitter_web_mcp.py
   ```

2. **The browser will try to open** (even if you can't see it)

3. **Find the browser process:**
   ```bash
   ps aux | grep chromium
   ```

4. **Alternative: Use Chrome/Edge on Windows**
   - Open Chrome/Edge on Windows
   - Navigate to `https://twitter.com` and log in
   - Copy the session data manually (advanced)

## Current Status

After my fixes:

✅ **Session directories now use project paths:**
- `.twitter_session/` (in project, not home directory)
- `.facebook_session/` (in project, not home directory)
- `.instagram_session/` (in project, not home directory)

✅ **Environment variables added to `.env`:**
```bash
TWITTER_SESSION_DIR=.twitter_session
FACEBOOK_SESSION_DIR=.facebook_session
INSTAGRAM_SESSION_DIR=.instagram_session
```

✅ **MCPs updated to use project-relative paths** (matching your WhatsApp MCP pattern)

❌ **Sessions not initialized yet** (browser window didn't show)

## Next Steps

**Recommended approach:**

1. **Use Windows PowerShell** to run the initialization:
   ```powershell
   cd D:\hackathon-0\My_AI_Employee
   .\scripts\setup\initialize_social_sessions.ps1 -Platform twitter
   ```

2. **Log in when browser opens**

3. **Verify from WSL:**
   ```bash
   cd /mnt/d/hackathon-0/My_AI_Employee
   ls -la .twitter_session/
   # Should show browser profile files
   ```

4. **Test the MCP:**
   ```bash
   uv run mcp dev mcp_servers/twitter_web_mcp.py
   # Then call: health_check
   # Should return: {"status": "healthy", "logged_in": true}
   ```

## Why This Matters

The session directories MUST be in the project directory because:

1. **Your code expects them there** (via `.env` variables)
2. **Git can ignore them** (add to `.gitignore`)
3. **Portable** - works when you move the project
4. **Consistent with WhatsApp MCP** - same architecture

The old directories in `/home/cyb3r/` were wrong and have been cleaned up.
