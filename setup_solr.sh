#!/bin/bash

# 1. Load configuration from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "📁 Loaded configuration from .env"
fi

# Variables
CONTAINER="oca_schema_solr"
CORE="${SOLR_CORE:-schemas-dj}"
BASE_URL="http://localhost:8984/solr"

echo "🚀 Starting Setup for Core: $CORE"

# 2. Cleanup & Filesystem Prep
# We ensure the physical folders exist so Solr doesn't fail on init
echo "🛠  Preparing container filesystem..."
docker exec -u root "$CONTAINER" mkdir -p /var/solr/data/"$CORE"/conf
docker exec -u root "$CONTAINER" cp -r /opt/solr/server/solr/configsets/_default/conf/. /var/solr/data/"$CORE"/conf/
docker exec -u root "$CONTAINER" chown -R solr:solr /var/solr/data/"$CORE"

# 3. Initialize Core
# We use 'create' which is smarter than the raw API for Docker environments
echo "📦 Initializing Solr Core..."
docker exec -u solr "$CONTAINER" solr create -c "$CORE" 2>/dev/null || echo "ℹ️  Core already exists, updating schema..."

# 4. Define Schema Fields (Including 'description')
echo "📡 Configuring Schema Fields..."

# We use the 'add-field' list. Solr 9+ handles this as a batch.
curl -s -X POST -H 'Content-type:application/json' --data-binary "{
  \"add-field\": [
    { \"name\": \"schema_id\", \"type\": \"string\", \"stored\": true, \"indexed\": true },
    { \"name\": \"schema_name\", \"type\": \"text_general\", \"stored\": true, \"indexed\": true },
    { \"name\": \"description\", \"type\": \"text_general\", \"stored\": true, \"indexed\": true },
    { \"name\": \"attributes\", \"type\": \"strings\", \"stored\": true, \"indexed\": true, \"multiValued\": true },
    { \"name\": \"attribute_count\", \"type\": \"pint\", \"stored\": true, \"indexed\": true }
  ]
}" "$BASE_URL/$CORE/schema" | grep -v "already exists" # Filter out noise if fields exist

echo "✨ All done! Your schema now supports descriptions."
echo "🔗 Admin UI: $BASE_URL/#/~cores/$CORE"