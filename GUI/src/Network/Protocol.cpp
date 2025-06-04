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
    initHandlers();
    _network->setMessageCallback([this](const ServerMessage &msg) {
        std::cout << "Command: " << msg.command << " " << msg.params << std::endl;

        GP cmd = getGuiProtocol(msg.command);

        try {
            _handlers[cmd](msg.params);
        } catch (const std::exception &e) {
            std::cerr << "Error handling command \"" + msg.command + " " + msg.params + "\": " << e.what() << std::endl;
        }
    });
}

zappy::network::Protocol::~Protocol() {
    disconnect();
}

void zappy::network::Protocol::initHandlers()
{
    _handlers = {
        {GP::MAP_SIZE,               [this](auto &p){ handleMapSize(p); }},
        {GP::TILE_CONTENT,           [this](auto &p){ handleTileContent(p); }},
        {GP::TEAM_NAME,              [this](auto &p){ handleTeamNames(p); }},
        {GP::NEW_PLAYER,             [this](auto &p){ handleNewPlayer(p); }},
        {GP::PLAYER_POSITION,        [this](auto &p){ handlePlayerPosition(p); }},
        {GP::PLAYER_LEVEL,           [this](auto &p){ handlePlayerLevel(p); }},
        {GP::PLAYER_INVENTORY,       [this](auto &p){ handlePlayerInventory(p); }},
        {GP::PLAYER_EXPULSION,       [this](auto &p){ handlePlayerExpulsion(p); }},
        {GP::PLAYER_BROADCAST,       [this](auto &p){ handlePlayerBroadcast(p); }},
        {GP::INCANTATION_START,      [this](auto &p){ handleIncantationStart(p); }},
        {GP::INCANTATION_END,        [this](auto &p){ handleIncantationEnd(p); }},
        {GP::EGG_LAYING,             [this](auto &p){ handleEggLaying(p); }},
        {GP::RESOURCE_DROP,          [this](auto &p){ handleResourceDrop(p); }},
        {GP::RESOURCE_COLLECT,       [this](auto &p){ handleResourceCollect(p); }},
        {GP::PLAYER_DEATH,           [this](auto &p){ handlePlayerDeath(p); }},
        {GP::EGG_CREATED,            [this](auto &p){ handleEggCreated(p); }},
        {GP::EGG_HATCH,              [this](auto &p){ handleEggHatch(p); }},
        {GP::EGG_DESTROYED,          [this](auto &p){ handleEggDeath(p); }},
        {GP::TIME_UNIT_REQUEST,      [this](auto &p){ handleTimeUnit(p); }},
        {GP::TIME_UNIT_MODIFICATION, [this](auto &p){ setTimeUnit(std::stoi(p)); }},
        {GP::GAME_END,               [this](auto &p){ handleGameEnd(p); }},
        {GP::SERVER_MESSAGE,         [this](auto &p){ handleServerMessage(p); }},
        {GP::UNKNOWN_COMMAND,        [](auto &){ std::cerr << "Server: Unknown command\n"; }},
        {GP::COMMAND_PARAMETER,      [](auto &){ std::cerr << "Server: Bad parameter\n"; }}
    };
}

void zappy::network::Protocol::onServerMessage(const ServerMessage &msg)
{
    GuiProtocol cmd = getGuiProtocol(msg.command);
    auto it = _handlers.find(cmd);

    if (it != _handlers.end())
        it->second(msg.params);
    else
        std::cerr << "Unhandled command: " << msg.command << std::endl;
}

bool zappy::network::Protocol::connectToServer(const std::string &host, int port) {
    try {
        if (!_network->connect(host, port))
            return false;

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

        // sent automatically
        // requestMapSize();
        // requestTimeUnit();
        // requestTeamNames();
        // std::this_thread::sleep_for(std::chrono::milliseconds(100));
        // requestMapContent();

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

// Handlers selon le protocole officiel
void zappy::network::Protocol::handleMapSize(const std::string &params)
{
    std::istringstream iss(params);
    size_t width;
    size_t height;

    iss >> width >> height;

    _gameState->initMap(width, height);
    std::cout << "Map size received: " << width << "x" << height << std::endl;
}

void zappy::network::Protocol::handleTileContent(const std::string &params)
{
    std::istringstream iss(params);
    int x;
    int y;

    iss >> x >> y;

    game::Tile tile;
    size_t resourceCount;
    for (size_t i = 0; i < game::RESOURCE_QUANTITY; ++i) {
        if (!(iss >> resourceCount)) {
            std::cerr << "Error parsing tile content" << std::endl;
            return;
        }
        tile.addResource(static_cast<game::Resource>(i), resourceCount);
    }

    _gameState->updateTile(x, y, tile);
}

void zappy::network::Protocol::handleTeamNames(const std::string &params)
{
    std::istringstream iss(params);
    std::string teamName;

    iss >> teamName;

    _gameState->addTeam(teamName);
    std::cout << "Team added: " << params << std::endl;
}

void zappy::network::Protocol::handleNewPlayer(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    std::string command;
    int playerId;
    size_t x, y;
    std::string orientation;
    size_t level;
    std::string teamName;

    iss >> command >> playerId >> x >> y >> orientation >> level >> teamName;

    game::Player player(
        playerId, x, y,
        game::convertOrientation(orientation),
        level
    );
    player.teamName = teamName;

    _gameState->addPlayer(player);
    std::cout << "New player " << player.id <<
        " connected from team " << player.teamName << std::endl;
}

void zappy::network::Protocol::handlePlayerPosition(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    size_t x, y;
    std::string orientation;

    iss >> playerId >> x >> y >> orientation;

    _gameState->updatePlayerPosition(playerId, x, y, game::convertOrientation(orientation));
}

void zappy::network::Protocol::handlePlayerLevel(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    size_t level;

    iss >> playerId >> level;

    _gameState->updatePlayerLevel(playerId, level);
    std::cout << "Player " << playerId << " reached level " << level << std::endl;
}

void zappy::network::Protocol::handlePlayerInventory(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;

    iss >> playerId;

    game::Inventory inventory;
    size_t resourceCount;
    for (size_t i = 0; i < game::RESOURCE_QUANTITY; ++i) {
        if (!(iss >> resourceCount)) {
            std::cerr << "Error parsing tile content" << std::endl;
            return;
        }
        inventory.addResource(static_cast<game::Resource>(i), resourceCount);
    }

    _gameState->updatePlayerInventory(playerId, inventory);
}

void zappy::network::Protocol::handleGameEnd(const std::string &params)
{
    std::istringstream iss(params);
    std::string winningTeam;

    iss >> winningTeam;

    _gameState->endGame(winningTeam);
    std::cout << "Game ended! Winning team: " << winningTeam << std::endl;
}

void zappy::network::Protocol::handlePlayerExpulsion(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;

    iss >> playerId;

    std::cout << "Player " << playerId << " was expelled" << std::endl;
}

void zappy::network::Protocol::handlePlayerBroadcast(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    std::string message;

    iss >> playerId >> message;

    // Log the broadcast message
    std::cout << "Player " << playerId << " broadcast: " << message << std::endl;
}

/**
 * @brief Handles the start of an incantation event
 *
 * Parses the incantation start parameters to extract the x and y coordinates
 * and the target level of the incantation. Logs the incantation details to
 * the console.
 *
 * @param params A string containing the incantation start parameters
 *               Expected format: "X Y L #n #n ..."
 */
void zappy::network::Protocol::handleIncantationStart(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    size_t x, y, level;
    std::vector<int> playerIds;

    iss >> x >> y >> level;

    // get player IDs from the rest of the string
    int playerId;
    while (iss >> playerId)
        playerIds.push_back(playerId);

    // handle the incantation
    std::cout << "Incantation started at (" << x << ", " << y << ") for level " << level << " with players:";
    for (const auto &playerId : playerIds)
        std::cout << " " << playerId;
    std::cout << std::endl;
}

/**
 * @brief Handles the end of an incantation event
 *
 * Parses the incantation end parameters to extract the x and y coordinates
 * and the success status of the incantation. Logs the incantation result
 * to the console.
 *
 * @param params A string containing the incantation end parameters
 *               Expected format: "X Y Result", where Result is 1 (true) or 0 (false)
 */
void zappy::network::Protocol::handleIncantationEnd(const std::string &params)
{
    std::istringstream iss(params);
    size_t x, y;
    bool success;

    iss >> x >> y >> success;

    std::cout << "Incantation " << (success ? "succeeded" : "failed")
                << " at (" << x << ", " << y << ")" << std::endl;
}

void zappy::network::Protocol::handleEggLaying(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;

    iss >> playerId;

    // animation
    std::cout << "Egg laid by player " << playerId << std::endl;
}

void zappy::network::Protocol::handleResourceDrop(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    size_t nbResources;

    iss >> playerId >> nbResources;

    // animation
    std::cout << "Player " << playerId << " dropped " << nbResources << " resources" << std::endl;
}

void zappy::network::Protocol::handleResourceCollect(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    size_t nbResources;

    iss >> playerId >> nbResources;

    // animation
    std::cout << "Player " << playerId << " collected " << nbResources << " resources" << std::endl;
}

void zappy::network::Protocol::handlePlayerDeath(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;

    iss >> playerId;

    _gameState->removePlayer(playerId);
    std::cout << "Player " << playerId << " died" << std::endl;
}

void zappy::network::Protocol::handleEggCreated(const std::string &params)
{
    std::istringstream iss(params);

    int eggId;
    int playerId;
    size_t x, y;

    iss >> eggId >> playerId >> x >> y;

    _gameState->addEgg(eggId, playerId, x, y);
    std::cout << "Egg created at (" << x << ", " << y << ") by player " << playerId << std::endl;
}

void zappy::network::Protocol::handleEggHatch(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int eggId;

    iss >> eggId;

    _gameState->hatchEgg(eggId);
    std::cout << "Egg " << eggId << " hatched" << std::endl;
}

void zappy::network::Protocol::handleEggDeath(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int eggId;

    iss >> eggId;

    _gameState->removeEgg(eggId);
    std::cout << "Egg " << eggId << " died" << std::endl;
}

void zappy::network::Protocol::handleTimeUnit(const std::string &params)
{
    std::istringstream iss(params);
    size_t timeUnit;

    iss >> timeUnit;

    _gameState->setFrequency(timeUnit);
    std::cout << "Time unit set to " << timeUnit << std::endl;
}

void zappy::network::Protocol::handleServerMessage(const std::string &params)
{
    std::cout << "Server message: " << params << std::endl;
}

void zappy::network::Protocol::removeSharp(std::string &message)
{
    size_t pos = message.find('#');

    while (pos != std::string::npos) {
        message.erase(pos, 1);
        pos = message.find('#');
    }
}
