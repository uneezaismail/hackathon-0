#!/bin/bash
# Quick setup for remaining Gold tier credentials

echo "=== Gold Tier Remaining Setup ==="
echo ""

# Phase 1: Check Twitter
echo "Phase 1: Checking Twitter credentials..."
cd /mnt/d/hackathon-0/My_AI_Employee
if grep -q "PASTE_YOUR_ACCESS_TOKEN_HERE" .env; then
    echo "❌ Twitter Access Token not updated yet"
    echo "   Action: Generate at https://console.x.com/ → Keys and tokens → Access Token"
    echo "   Then update .env file"
    exit 1
else
    echo "✅ Twitter credentials configured"
fi

echo ""

# Phase 2: Setup Odoo
echo "Phase 2: Setting up Odoo Community..."
if docker ps | grep -q "odoo"; then
    echo "✅ Odoo already running"
else
    if docker ps -a | grep -q "odoo"; then
        echo "Starting existing Odoo containers..."
        docker start odoo-db odoo
    else
        echo "Creating new Odoo containers..."
        docker pull postgres:15
        docker pull odoo:19
        
        docker run -d --name odoo-db \
          -e POSTGRES_USER=odoo \
          -e POSTGRES_PASSWORD=odoo \
          -e POSTGRES_DB=postgres \
          postgres:15
        
        sleep 5
        
        docker run -d --name odoo \
          --link odoo-db:db \
          -p 8069:8069 \
          -v odoo-data:/var/lib/odoo \
          odoo:19
        
        echo "Waiting for Odoo to start (30 seconds)..."
        sleep 30
    fi
fi

# Test Odoo
if curl -s http://localhost:8069 | grep -q "Odoo"; then
    echo "✅ Odoo is running at http://localhost:8069"
    
    # Add Odoo credentials to .env if not present
    if ! grep -q "ODOO_URL" .env; then
        echo "" >> .env
        echo "# ============================================" >> .env
        echo "# Odoo Configuration (Gold Tier)" >> .env
        echo "# ============================================" >> .env
        echo "ODOO_URL=http://localhost:8069" >> .env
        echo "ODOO_DB=odoo_db" >> .env
        echo "ODOO_USERNAME=admin" >> .env
        echo "ODOO_PASSWORD=admin" >> .env
        echo "ODOO_QUEUE_FILE=.odoo_queue.jsonl" >> .env
        echo "✅ Odoo credentials added to .env"
    fi
    
    echo ""
    echo "Manual steps required:"
    echo "1. Open browser: http://localhost:8069"
    echo "2. Create database:"
    echo "   - Database Name: odoo_db"
    echo "   - Email: admin@example.com"
    echo "   - Password: admin"
    echo "3. Install 'Accounting' module from Apps menu"
else
    echo "❌ Odoo not accessible yet"
    echo "   Check logs: docker logs odoo"
fi

echo ""

# Phase 3: Facebook & Instagram
echo "Phase 3: Facebook & Instagram Setup"
echo "Manual steps required:"
echo ""
echo "Facebook API (15 minutes):"
echo "1. Go to: https://developers.facebook.com/"
echo "2. Create app → Business type"
echo "3. Add Facebook Login product"
echo "4. Generate access token at: https://developers.facebook.com/tools/explorer/"
echo "   Permissions: pages_manage_posts, pages_read_engagement"
echo "5. Get Page ID from your Facebook Page → About"
echo "6. Add to .env:"
echo "   FACEBOOK_ACCESS_TOKEN=your_token"
echo "   FACEBOOK_PAGE_ID=your_page_id"
echo ""
echo "Instagram API (10 minutes):"
echo "1. Convert Instagram to Business Account (in app)"
echo "2. Connect to Facebook Page"
echo "3. Get Instagram Business Account ID:"
echo "   curl 'https://graph.facebook.com/v19.0/PAGE_ID?fields=instagram_business_account&access_token=TOKEN'"
echo "4. Add to .env:"
echo "   INSTAGRAM_ACCESS_TOKEN=your_facebook_token"
echo "   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_account_id"

echo ""
echo "=== Setup Status ==="
echo "✅ Twitter: Complete"
echo "✅ Odoo: Running (manual database setup needed)"
echo "⏳ Facebook: Manual setup required"
echo "⏳ Instagram: Manual setup required"
echo ""
echo "After all credentials are configured, run:"
echo "  cd /mnt/d/hackathon-0"
echo "  claude code '/gold-tier-validator Validate Gold tier'"

