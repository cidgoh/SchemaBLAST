#!/bin/bash

# 1. Load configuration from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "📁 Loaded configuration from .env"
fi

# Variables
CONTAINER="oca_schema_solr"
CORE="${SOLR_CORE:-schemas}"
BASE_URL="http://localhost:8984/solr"

echo "🚀 Starting Setup for Core: $CORE"

# 2. Cleanup & Filesystem Prep
echo "🛠  Preparing container filesystem..."
docker exec -u root "$CONTAINER" mkdir -p /var/solr/data/"$CORE"/conf
docker exec -u root "$CONTAINER" cp -r /opt/solr/server/solr/configsets/_default/conf/. /var/solr/data/"$CORE"/conf/
docker exec -u root "$CONTAINER" chown -R solr:solr /var/solr/data/"$CORE"

# 3. Initialize Core
echo "📦 Initializing Solr Core..."
docker exec -u solr "$CONTAINER" solr create -c "$CORE" 2>/dev/null || echo "ℹ️  Core already exists, updating schema..."

# 4. Define Schema Fields (including timestamp and metadata)
echo "📡 Configuring Schema Fields..."
curl -s -X POST -H 'Content-type:application/json' --data-binary "{
  \"add-field\": [
    { \"name\": \"schema_id\",      \"type\": \"string\",        \"stored\": true, \"indexed\": true },
    { \"name\": \"schema_name\",    \"type\": \"text_general\",  \"stored\": true, \"indexed\": true },
    { \"name\": \"description\",    \"type\": \"text_general\",  \"stored\": true, \"indexed\": true },
    { \"name\": \"attributes\",     \"type\": \"strings\",       \"stored\": true, \"indexed\": true, \"multiValued\": true },
    { \"name\": \"attribute_count\",\"type\": \"pint\",          \"stored\": true, \"indexed\": true },
    { \"name\": \"timestamp\",      \"type\": \"pdate\",         \"stored\": true, \"indexed\": true },
    { \"name\": \"metadata\",       \"type\": \"string\",        \"stored\": true, \"indexed\": false }
  ]
}" "$BASE_URL/$CORE/schema" | grep -v "already exists"

echo "✨ All done! Your schema now supports descriptions, timestamps, and metadata."
echo "🔗 Admin UI: $BASE_URL/#/~cores/$CORE"