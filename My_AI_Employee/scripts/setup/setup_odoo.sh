#!/bin/bash
# Odoo Community Setup Script

echo "=== Odoo Community Setup ==="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"
    echo "Install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo "  sudo usermod -aG docker $USER"
    echo "  # Log out and back in"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Check if Odoo containers already exist
if docker ps -a | grep -q "odoo"; then
    echo "⚠️ Odoo containers already exist"
    echo "Starting existing containers..."
    docker start odoo-db 2>/dev/null
    docker start odoo 2>/dev/null
else
    echo "Creating new Odoo containers..."
    echo ""

    # Pull images
    echo "1. Pulling Docker images..."
    docker pull postgres:15
    docker pull odoo:19

    # Create PostgreSQL container
    echo ""
    echo "2. Creating PostgreSQL database..."
    docker run -d \
      --name odoo-db \
      -e POSTGRES_USER=odoo \
      -e POSTGRES_PASSWORD=odoo \
      -e POSTGRES_DB=postgres \
      postgres:15

    # Wait for PostgreSQL to start
    echo "Waiting for PostgreSQL to start..."
    sleep 5

    # Create Odoo container
    echo ""
    echo "3. Creating Odoo container..."
    docker run -d \
      --name odoo \
      --link odoo-db:db \
      -p 8069:8069 \
      -v odoo-data:/var/lib/odoo \
      odoo:19

    echo ""
    echo "4. Waiting for Odoo to start (30 seconds)..."
    sleep 30
fi

# Test Odoo access
echo ""
echo "5. Testing Odoo access..."
if curl -s http://localhost:8069 | grep -q "Odoo"; then
    echo "✅ Odoo is running!"
    echo ""
    echo "Next steps:"
    echo "1. Open browser: http://localhost:8069"
    echo "2. Create database:"
    echo "   - Database Name: odoo_db"
    echo "   - Email: admin@example.com"
    echo "   - Password: admin"
    echo "3. Install 'Accounting' module from Apps menu"
    echo ""
    echo "After setup, add to .env:"
    echo "ODOO_URL=http://localhost:8069"
    echo "ODOO_DB=odoo_db"
    echo "ODOO_USERNAME=admin"
    echo "ODOO_PASSWORD=admin"
    echo "ODOO_QUEUE_FILE=.odoo_queue.jsonl"
else
    echo "❌ Odoo not accessible yet"
    echo "Check logs: docker logs odoo"
    echo "Wait a bit longer and try: curl http://localhost:8069"
fi

echo ""
echo "=== Odoo Setup Complete ==="
