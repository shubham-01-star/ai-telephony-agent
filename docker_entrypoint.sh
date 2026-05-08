#!/bin/bash
set -e

echo "Starting AI Telephony Agent Entrypoint..."

# Check if VIDEOSDK_API_KEY and VIDEOSDK_SECRET_KEY are set
if [ -n "$VIDEOSDK_API_KEY" ] && [ -n "$VIDEOSDK_SECRET_KEY" ]; then
    echo "Generating fresh VIDEOSDK_AUTH_TOKEN..."
    # Run the generate_token script and extract the token
    # We use python3 -c to avoid needing to save a temporary file if we wanted to be fancy, 
    # but we already have generate_token.py
    TOKEN=$(python3 generate_token.py rtc | grep -v "Role:" | grep -v "\-\-\-\-" | grep -v "Update .env:" | xargs)
    
    if [ -n "$TOKEN" ]; then
        export VIDEOSDK_AUTH_TOKEN=$TOKEN
        echo "Successfully generated and exported VIDEOSDK_AUTH_TOKEN."
    else
        echo "Warning: Failed to generate VIDEOSDK_AUTH_TOKEN automatisch."
    fi
else
    echo "Notice: VIDEOSDK_API_KEY or VIDEOSDK_SECRET_KEY missing. Using VIDEOSDK_AUTH_TOKEN from environment if available."
fi

# Execute the main application
echo "Starting main.py..."
exec python3 main.py
