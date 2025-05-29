/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NetworkManager.cpp
*/

#include "NetworkManager.hpp"

zappy::network::NetworkManager::NetworkManager() :
    _socket(-1),
    _connected(false)
{}

zappy::network::NetworkManager::~NetworkManager()
{
    disconnect();
}

bool zappy::network::NetworkManager::connect(const std::string& host, int port) {
    _socket = socket(AF_INET, SOCK_STREAM, 0);
    if (_socket == -1) {
        throw NetworkError("Failed to create socket", "Network");
    }

    struct sockaddr_in serverAddr;
    std::memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);

    if (inet_pton(AF_INET, host.c_str(), &serverAddr.sin_addr) <= 0) {
        close(_socket);
        _socket = -1;
        throw NetworkError("Invalid IP address: " + host, "Network");
    }

    if (::connect(_socket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        close(_socket);
        _socket = -1;
        throw NetworkError("Failed to connect to " + host + ":" + std::to_string(port), "Network");
    }

    _connected = true;
    return true;
}

void zappy::network::NetworkManager::disconnect()
{
    if (_socket != -1) {
        close(_socket);
        _socket = -1;
    }
    _connected = false;
}

bool zappy::network::NetworkManager::isConnected() const
{
    return _connected;
}

bool zappy::network::NetworkManager::sendCommand(const std::string& command)
{
    if (!_connected || _socket == -1)
        return false;

    std::string fullCommand = command + "\n";
    ssize_t sent = send(_socket, fullCommand.c_str(), fullCommand.length(), 0);

    if (sent != static_cast<ssize_t>(fullCommand.length())) {
        _connected = false;
        return false;
    }

    return true;
}

std::vector<zappy::network::ServerMessage> zappy::network::NetworkManager::receiveMessages()
{
    std::lock_guard<std::mutex> lock(_mutex);

    if (!_connected || _socket == -1)
        return {};

    // Poll pour vérifier s'il y a des données (non-bloquant)
    struct pollfd pfd;
    pfd.fd = _socket;
    pfd.events = POLLIN;

    int pollResult = poll(&pfd, 1, 0);
    if (pollResult <= 0)
        return {};

    char buffer[4096];
    ssize_t received = recv(_socket, buffer, sizeof(buffer) - 1, 0);

    if (received <= 0) {
        _connected = false;
        return {};
    }

    buffer[received] = '\0';
    _buffer += buffer;

    processBuffer();

    std::vector<ServerMessage> messages;
    while (!_messageQueue.empty()) {
        messages.push_back(_messageQueue.front());
        _messageQueue.pop();
    }

    return messages;
}

void zappy::network::NetworkManager::processBuffer()
{
    size_t pos = 0;
    while ((pos = _buffer.find('\n')) != std::string::npos) {
        std::string line = _buffer.substr(0, pos);
        _buffer.erase(0, pos + 1);

        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }

        if (!line.empty()) {
            ServerMessage msg = parseMessage(line);
            _messageQueue.push(msg);

            if (_messageCallback) {
                _messageCallback(msg);
            }
        }
    }
}

zappy::network::ServerMessage zappy::network::NetworkManager::parseMessage(const std::string& raw)
{
    ServerMessage msg;
    msg.raw = raw;

    std::istringstream iss(raw);
    std::string token;

    if (iss >> token) {
        msg.command = token;
        while (iss >> token) {
            msg.params.push_back(token);
        }
    }

    return msg;
}

void zappy::network::NetworkManager::setMessageCallback(std::function<void(const ServerMessage&)> callback)
{
    _messageCallback = callback;
}
