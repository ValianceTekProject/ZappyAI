/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Protocol.cpp
*/

#include "Protocol.hpp"

zappy::network::Protocol::Protocol(std::shared_ptr<game::GameState> gameState)  :
    _network(std::make_unique<NetworkManager>()),
    _gameState(gameState),
    _authenticated(false)
{
    _network->setMessageCallback([this](const ServerMessage &msg) {
        if (msg.command == "msz")
            handleMapSize(msg.params);
        else if (msg.command == "bct")
            handleTileContent(msg.params);
        else if (msg.command == "tna")
            handleTeamNames(msg.params);
        else if (msg.command == "pnw")
            handleNewPlayer(msg.params);
        else if (msg.command == "ppo")
            handlePlayerPosition(msg.params);
        else if (msg.command == "plv")
            handlePlayerLevel(msg.params);
        else if (msg.command == "pin")
            handlePlayerInventory(msg.params);
        else if (msg.command == "pex")
            handlePlayerExpulsion(msg.params);
        else if (msg.command == "pbc")
            handlePlayerBroadcast(msg.params);
        else if (msg.command == "pic")
            handleIncantationStart(msg.params);
        else if (msg.command == "pie")
            handleIncantationEnd(msg.params);
        else if (msg.command == "pfk")
            handleEggLaying(msg.params);
        else if (msg.command == "pdr")
            handleResourceDrop(msg.params);
        else if (msg.command == "pgt")
            handleResourceCollect(msg.params);
        else if (msg.command == "pdi")
            handlePlayerDeath(msg.params);
        else if (msg.command == "enw")
            handleEggCreated(msg.params);
        else if (msg.command == "ebo")
            handleEggHatch(msg.params);
        else if (msg.command == "edi")
            handleEggDeath(msg.params);
        else if (msg.command == "sgt")
            handleTimeUnit(msg.params);
        else if (msg.command == "seg")
            handleGameEnd(msg.params);
        else if (msg.command == "smg")
            handleServerMessage(msg.params);
        else if (msg.command == "suc")
            std::cout << "Server: Unknown command" << std::endl;
        else if (msg.command == "sbp")
            std::cout << "Server: Bad command parameter" << std::endl;
    });
}

zappy::network::Protocol::~Protocol() {
    disconnect();
}

bool zappy::network::Protocol::connectToServer(const std::string &host, int port) {
    try {
        if (!_network->connect(host, port)) {
            return false;
        }

        std::vector<ServerMessage> messages;
        int attempts = 0;
        const int maxAttempts = 200;

        while (attempts < maxAttempts && messages.empty()) {
            messages = _network->receiveMessages();
            if (messages.empty()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
                attempts++;
            }
        }

        if (messages.empty() || messages[0].raw != "WELCOME") {
            std::cerr << "Failed to receive WELCOME message from server" << std::endl;
            _network->disconnect();
            return false;
        }

        std::cout << "Received: " << messages[0].raw << std::endl;

        // Envoyer "GRAPHIC" pour s'authentifier comme GUI
        if (!_network->sendCommand("GRAPHIC")) {
            std::cerr << "Failed to send GRAPHIC authentication" << std::endl;
            _network->disconnect();
            return false;
        }

        std::cout << "Sent: GRAPHIC" << std::endl;
        _authenticated = true;

        requestMapSize();
        requestTeamNames();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        requestMapContent();

        return true;

    } catch (const NetworkError &e) {
        std::cerr << e.where() << " Error: " << e.what() << std::endl;
        return false;
    }
}

void zappy::network::Protocol::disconnect() {
    _authenticated = false;
    _network->disconnect();
}

bool zappy::network::Protocol::isConnected() const {
    return _network->isConnected() && _authenticated;
}

void zappy::network::Protocol::update() {
    if (!isConnected())
        return;

    auto messages = _network->receiveMessages();
    // Les messages sont déjà traités par les callbacks configurés dans le constructeur
}

// Implémentation des handlers selon le protocole Zappy GUI
void zappy::network::Protocol::handleMapSize(const std::string &params) {
    if (params.size() >= 2) {
        try {
            int width = std::stoi(params[0]);
            int height = std::stoi(params[1]);
            _gameState->initMap(width, height);
            std::cout << "Map size received: " << width << "x" << height << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing map size: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handleTileContent(const std::string &params) {
    if (params.size() >= 9) {
        try {
            int x = std::stoi(params[0]);
            int y = std::stoi(params[1]);

            game::Tile resources;
            for (int i = 0; i < 7; ++i)
                resources.addResource(static_cast<game::Resource>(i), std::stoi(params[i + 2]));

            _gameState->updateTile(x, y, resources);
        } catch (const std::exception &e) {
            std::cerr << "Error parsing tile content: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handleTeamNames(const std::string &params)
{
    if (!params.empty()) {
        _gameState->addTeam(params[0]);
        std::cout << "Team added: " << params[0] << std::endl;
    }
}

void zappy::network::Protocol::handleNewPlayer(const std::string &params)
{
    if (params.size() >= 6) {
        try {
            std::istringstream iss(params);
            std::string command;
            size_t playerId;
            size_t x, y;
            std::string orientation;
            size_t level;
            std::string teamName;

            iss >> command >> playerId >> x >> y >> orientation >> level >> teamName;

            game::Player player(
                playerId, x, y,
                game::convertOrientation(orientation),
                level, teamName
            );

            _gameState->addPlayer(player);
            std::cout << "New player " << player.id << " connected from team "
                      << player.teamName << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing new player: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handlePlayerPosition(const std::string &params)
{
    if (params.size() >= 4) {
        try {
            int playerId = std::stoi(params[0].substr(1));
            int x = std::stoi(params[1]);
            int y = std::stoi(params[2]);
            game::Orientation orientation = static_cast<game::Orientation>(std::stoi(params[3]));

            _gameState->updatePlayerPosition(playerId, x, y, orientation);
        } catch (const std::exception &e) {
            std::cerr << "Error parsing player position: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handlePlayerLevel(const std::string &params)
{
    if (params.size() >= 2) {
        try {
            int playerId = std::stoi(params[0].substr(1));
            int level = std::stoi(params[1]);

            _gameState->updatePlayerLevel(playerId, level);
            std::cout << "Player " << playerId << " reached level " << level << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing player level: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handlePlayerInventory(const std::string &params)
{
    if (params.size() >= 10) {
        try {
            int playerId = std::stoi(params[0].substr(1));

            game::Inventory inventory;
            for (int i = 0; i < 7; ++i)
                inventory.addResource(static_cast<game::Resource>(i), std::stoi(params[i + 1]));

            _gameState->updatePlayerInventory(playerId, inventory);
        } catch (const std::exception &e) {
            std::cerr << "Error parsing player inventory: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handleGameEnd(const std::string &params)
{
    if (!params.empty()) {
        std::string winningTeam = params[0];
        _gameState->endGame(winningTeam);
        std::cout << "Game ended! Winning team: " << winningTeam << std::endl;
    }
}

// Commandes GUI vers serveur selon le protocole officiel
void zappy::network::Protocol::requestMapSize()
{
    _network->sendCommand("msz");
}

void zappy::network::Protocol::requestTileContent(int x, int y)
{
    _network->sendCommand("bct " + std::to_string(x) + " " + std::to_string(y));
}

void zappy::network::Protocol::requestMapContent()
{
    _network->sendCommand("mct");
}

void zappy::network::Protocol::requestTeamNames()
{
    _network->sendCommand("tna");
}

void zappy::network::Protocol::requestPlayerPosition(int playerId)
{
    _network->sendCommand("ppo #" + std::to_string(playerId));
}

void zappy::network::Protocol::requestPlayerLevel(int playerId)
{
    _network->sendCommand("plv #" + std::to_string(playerId));
}

void zappy::network::Protocol::requestPlayerInventory(int playerId)
{
    _network->sendCommand("pin #" + std::to_string(playerId));
}

void zappy::network::Protocol::requestTimeUnit()
{
    _network->sendCommand("sgt");
}

void zappy::network::Protocol::setTimeUnit(int timeUnit)
{
    _network->sendCommand("sst " + std::to_string(timeUnit));
}

// Handlers pour les autres événements (stub implementations pour l'instant)
void zappy::network::Protocol::handlePlayerExpulsion(const std::string &params)
{
    if (!params.empty()) {
        try {
            int playerId = std::stoi(params[0].substr(1));
            std::cout << "Player " << playerId << " was expelled" << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing player expulsion: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handlePlayerBroadcast(const std::string &params) {
    if (params.size() >= 2) {
        try {
            int playerId = std::stoi(params[0].substr(1));
            std::string message = params[1];
            std::cout << "Player " << playerId << " broadcast: " << message << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing player broadcast: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handleIncantationStart(const std::string &params) {
    if (params.size() >= 3) {
        try {
            int x = std::stoi(params[0]);
            int y = std::stoi(params[1]);
            int level = std::stoi(params[2]);
            std::cout << "Incantation started at (" << x << ", " << y << ") for level " << level << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing incantation start: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handleIncantationEnd(const std::string &params) {
    if (params.size() >= 3) {
        try {
            int x = std::stoi(params[0]);
            int y = std::stoi(params[1]);
            bool success = (params[2] == "1");
            std::cout << "Incantation " << (success ? "succeeded" : "failed")
                      << " at (" << x << ", " << y << ")" << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing incantation end: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handlePlayerDeath(const std::string &params) {
    if (!params.empty()) {
        try {
            int playerId = std::stoi(params[0].substr(1));

            _gameState->removePlayer(playerId);
            std::cout << "Player " << playerId << " died" << std::endl;
        } catch (const std::exception &e) {
            std::cerr << "Error parsing player death: " << e.what() << std::endl;
        }
    }
}

void zappy::network::Protocol::handleEggLaying(const std::string &params) {}
void zappy::network::Protocol::handleResourceDrop(const std::string &params) {}
void zappy::network::Protocol::handleResourceCollect(const std::string &params) {}
void zappy::network::Protocol::handleEggCreated(const std::string &params) {}
void zappy::network::Protocol::handleEggHatch(const std::string &params) {}
void zappy::network::Protocol::handleEggDeath(const std::string &params) {}
void zappy::network::Protocol::handleTimeUnit(const std::string &params) {}
void zappy::network::Protocol::handleServerMessage(const std::string &params) {}
void zappy::network::Protocol::handleMapContent(const std::string &params) {}
