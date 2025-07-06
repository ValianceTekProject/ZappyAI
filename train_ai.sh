#!/bin/bash

SERVER_EXEC="./zappy_server"
SERVER_CMD="$SERVER_EXEC -p 4000 -x 10 -y 10 -n red green -c 150 -f 100 --auto-start on"
CLIENT_CMD="python3 Client/client.py --port 4000 --team red --model PPO"

echo "Server launch"
$SERVER_CMD &
SERVER_PID=$!
trap "echo 'Server Stop...'; kill $SERVER_PID; exit" SIGINT SIGTERM

sleep 3

while true; do
    echo "IA launch"
    $CLIENT_CMD
    echo "IA Stop"
    sleep 1
done

