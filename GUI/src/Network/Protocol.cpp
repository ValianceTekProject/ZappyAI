/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Protocol.cpp
*/

#include "Protocol.hpp"

zappy::network::Protocol::Protocol(
    std::shared_ptr<gui::IRenderer> renderer,
    std::shared_ptr<game::GameState> gameState,
    bool debug
) : _debug(debug),
    _network(std::make_unique<NetworkManager>()),
    _renderer(renderer),
    _gameState(gameState),
    _authenticated(false)
{
    initHandlers();
    _network->setMessageCallback([this](const ServerMessage &msg) {
        printDebug("Received message: " + msg.command + " " + msg.params);

        GP cmd = getGuiProtocol(msg.command);

        try {
            _handlers[cmd](msg.params);
        } catch (const std::exception &e) {
            printDebug("Error handling command \"" + msg.command + " " + msg.params + "\": " + e.what(), std::cerr);
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
        {GP::UNKNOWN_COMMAND,        [this](auto &p){ handleUnknownCommand(p); }},
        {GP::COMMAND_PARAMETER,      [this](auto &p){ handleBadCommand(p); }}
    };
}

void zappy::network::Protocol::onServerMessage(const ServerMessage &msg)
{
    GuiProtocol cmd = getGuiProtocol(msg.command);
    auto it = _handlers.find(cmd);

    if (it != _handlers.end())
        it->second(msg.params);
    else
        printDebug("Unknown command: " + msg.command, std::cerr);
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
            printDebug("Failed to receive WELCOME message from server", std::cerr);
            _network->disconnect();
            return false;
        }

        printDebug("Received: " + messages[0].raw);

        // Envoyer "GRAPHIC" pour s'authentifier comme GUI
        if (!_network->sendCommand("GRAPHIC")) {
            printDebug("Failed to send GRAPHIC command to server", std::cerr);
            _network->disconnect();
            return false;
        }

        printDebug("Sent: GRAPHIC");
        _authenticated = true;

        // sent automatically
        // requestMapSize();
        // requestTimeUnit();
        // requestTeamNames();
        // std::this_thread::sleep_for(std::chrono::milliseconds(100));
        // requestMapContent();

        return true;

    } catch (const NetworkError &e) {
        printDebug(e.where() + std::string(" error: ") + e.what(), std::cerr);
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
    _renderer->init();
    printDebug("Map size: " + std::to_string(width) + "x" + std::to_string(height));
}

/**
 * @brief Handles the content of a specific tile on the game map
 *
 * Parses the tile's coordinates and resource quantities, creating a Tile object
 * with the parsed resources. Updates the game state with the new tile information.
 *
 * @param params A string containing tile coordinates and resource quantities
 *               Format: "X Y R1 R2 R3 R4 R5 R6"
 *               Where X, Y are coordinates and R1-R6 are resource quantities
 */
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
            printDebug("Error parsing tile content", std::cerr);
            return;
        }
        tile.addResource(static_cast<game::Resource>(i), resourceCount);
    }

    _gameState->updateTile(x, y, tile);
}

/**
 * @brief Handle the team names received from the server.
 *
 * Parses the team name from the received parameters and adds it to the game state.
 * Prints a debug message indicating the team has been added.
 *
 * @param params A string containing the team name
 */
void zappy::network::Protocol::handleTeamNames(const std::string &params)
{
    std::istringstream iss(params);
    std::string teamName;

    iss >> teamName;

    _gameState->addTeam(teamName);
    printDebug("Team " + teamName + " added");
}

/**
 * @brief Handles the event of a new player joining the game
 *
 * Parses the new player parameters to extract the player ID, position, orientation,
 * level, and team name. Creates a new Player object and adds it to the renderer.
 *
 * @param params A string containing the new player's details
 *               Example: "#n X Y N L TeamName"
 */
void zappy::network::Protocol::handleNewPlayer(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    int x, y;
    size_t orientation;
    size_t level;
    std::string teamName;

    iss >> playerId >> x >> y >> orientation >> level >> teamName;

    game::Player player(
        playerId, x, y,
        static_cast<game::Orientation>(orientation - 1),
        level
    );
    player.teamName = teamName;

    _renderer->addPlayer(player);
    printDebug("New player " + std::to_string(playerId) + " connected from team " + teamName);
}

/**
 * @brief Handle the player's position update event.
 *
 * Parses the player position parameters to extract the player ID, position, and orientation.
 * Updates the renderer with the player's position and orientation.
 *
 * @param params A string containing the player ID, position, and orientation
 *               Example: "#n X Y O"
 */
void zappy::network::Protocol::handlePlayerPosition(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    int x, y;
    size_t orientation;

    iss >> playerId >> x >> y >> orientation;

    _renderer->updatePlayerPosition(playerId, x, y, static_cast<game::Orientation>(orientation - 1));
}

/**
 * @brief Handles a player's level update event
 *
 * Parses the level update parameters to extract the player ID and new level.
 * Updates the renderer with the player's new level and logs the level change.
 *
 * @param params A string containing the player ID and their new level
 *               Example: "#n L"
 */
void zappy::network::Protocol::handlePlayerLevel(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    size_t level;

    iss >> playerId >> level;

    _renderer->updatePlayerLevel(playerId, level);
    printDebug("Player " + std::to_string(playerId) + " reached level " + std::to_string(level));
}

/**
 * @brief Handles a player's inventory update
 *
 * Parses the inventory parameters to extract the player ID and resource quantities.
 * Removes the leading '#' from the parameters and creates an inventory object.
 * Updates the renderer with the player's new inventory.
 *
 * @param params A string containing the player's inventory information
 *               Expected format: "#n resource1 resource2 ... resourceN"
 */
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
            printDebug("Error parsing player inventory", std::cerr);
            return;
        }
        inventory.addResource(static_cast<game::Resource>(i), resourceCount);
    }

    _renderer->updatePlayerInventory(playerId, inventory);
}

/**
 * @brief Handles the end of the game
 *
 * Parses the game end parameters to extract the winning team.
 * Notifies the renderer about the game's conclusion and prints the winning team.
 *
 * @param params A string containing the name of the winning team
 *               Expected format: "TeamName"
 */
void zappy::network::Protocol::handleGameEnd(const std::string &params)
{
    std::istringstream iss(params);
    std::string winningTeam;

    iss >> winningTeam;

    _renderer->endGame(winningTeam);
    std::cout << "Game ended! Winning team: " << winningTeam << std::endl;
}

/**
 * @brief Handles a player expulsion event
 *
 * Parses the expulsion parameters to extract the player ID.
 * Logs the expulsion details to the console.
 *
 * @param params A string containing the expulsion parameters
 *               Expected format: "#n"
 */
void zappy::network::Protocol::handlePlayerExpulsion(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;

    iss >> playerId;

    _renderer->PlayerExpulsion(playerId);
    printDebug("Player " + std::to_string(playerId) + " expelled");
}

/**
 * @brief Handles a player broadcast message
 *
 * Parses the broadcast parameters to extract the player ID and message.
 * Removes the leading '#' from the parameters and logs the broadcast
 * message to the console.
 *
 * @param params A string containing the broadcast parameters
 *               Expected format: "#n Message"
 */
void zappy::network::Protocol::handlePlayerBroadcast(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    std::string message;

    iss >> playerId >> message;

    _renderer->PlayerBroadcast(playerId, message);
    printDebug("Player " + std::to_string(playerId) + " broadcast: " + message);
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

    _renderer->StartIncantation(x, y, level, playerIds);
    std::string result;
    result += "Incantation started at (" + std::to_string(x) + ", " + std::to_string(y) + ") for level " + std::to_string(level) + " with players:";
    for (const auto &playerId : playerIds)
        result += " " + std::to_string(playerId);
    printDebug(result);
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

    _renderer->EndIncantation(x, y, success);
    printDebug("Incantation " + std::string(success ? "succeeded" : "failed") + " at (" + std::to_string(x) + ", " + std::to_string(y) + ")");
}

/**
 * @brief Handles the egg laying event for a specific player
 *
 * Parses the egg laying parameters to extract the player ID
 * and logs the egg laying event to the console.
 *
 * @param params A string containing the player ID who laid the egg
 *               Expected format: "#n"
 */
void zappy::network::Protocol::handleEggLaying(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;

    iss >> playerId;

    // animation
    printDebug("Egg laid by player " + std::to_string(playerId));
}

/**
 * @brief Handles the resource drop event for a specific player
 *
 * Parses the resource drop parameters to extract the player ID
 * and the number of resources dropped, and logs the event to the console.
 *
 * @param params A string containing the player ID and number of resources
 *               Expected format: "#n NbResources"
 */
void zappy::network::Protocol::handleResourceDrop(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    size_t nbResources;

    iss >> playerId >> nbResources;

    // animation
    printDebug("Player " + std::to_string(playerId) + " dropped " + std::to_string(nbResources) + " resources");
}

/**
 * @brief Handles the resource collection event for a specific player
 *
 * Parses the resource collection parameters to extract the player ID
 * and the number of resources collected, and logs the event to the console.
 *
 * @param params A string containing the player ID and number of resources
 *               Expected format: "#n NbResources"
 */
void zappy::network::Protocol::handleResourceCollect(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;
    size_t nbResources;

    iss >> playerId >> nbResources;

    // animation
    printDebug("Player " + std::to_string(playerId) + " collected " + std::to_string(nbResources) + " resources");
}

/**
 * @brief Handles the player death event for a specific player
 *
 * Parses the player death parameters to extract the player ID
 *
 * @param params A string containing the player ID who died
 *               Expected format: "#n"
 */
void zappy::network::Protocol::handlePlayerDeath(const std::string &params)
{
    // remove # from the beginning of the string
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int playerId;

    iss >> playerId;

    _renderer->removePlayer(playerId);
    printDebug("Player " + std::to_string(playerId) + " died");
}

/**
 * @brief Handles the egg spawn event by a specific player
 *
 * Parses the player respawn parameters to extract the player ID
 *
 * @param params A string containing the player ID who respawned
 *                Expected format: "EggID n X Y"
 */
void zappy::network::Protocol::handleEggCreated(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);

    int eggId;
    int playerId;
    int x, y;

    iss >> eggId >> playerId >> x >> y;

    _renderer->addEgg(eggId, playerId, x, y);
    printDebug("Egg " + std::to_string(eggId) + " created at (" + std::to_string(x) + ", " + std::to_string(y) + ") by player " + std::to_string(playerId));
}

/**
 * @brief Handles a player spawn event
 *
 * Parses the player respawn parameters to extract the player ID
 *
 * @param params A string containing the EggID where the egg was hatched
 *                Expected format: "EggID"
 */
void zappy::network::Protocol::handleEggHatch(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int eggId;

    iss >> eggId;

    _renderer->hatchEgg(eggId);
    printDebug("Egg " + std::to_string(eggId) + " hatched");
}

void zappy::network::Protocol::handleEggDeath(const std::string &params)
{
    std::string trueParams = params;
    removeSharp(trueParams);

    std::istringstream iss(trueParams);
    int eggId;

    iss >> eggId;

    _renderer->removeEgg(eggId);
    printDebug("Egg " + std::to_string(eggId) + " died");
}

void zappy::network::Protocol::handleTimeUnit(const std::string &params)
{
    std::istringstream iss(params);
    size_t timeUnit;

    iss >> timeUnit;

    _gameState->setFrequency(timeUnit);
    printDebug("Time unit set to " + std::to_string(timeUnit));
}

void zappy::network::Protocol::handleServerMessage(const std::string &params)
{
    printDebug("Server message: " + params);
}

void zappy::network::Protocol::handleUnknownCommand(const std::string &params)
{
    printDebug("Unknown command: " + params);
}

void zappy::network::Protocol::handleBadCommand(const std::string &params)
{
    printDebug("Bad command: " + params);
}

void zappy::network::Protocol::removeSharp(std::string &message)
{
    size_t pos = message.find('#');

    while (pos != std::string::npos) {
        message.erase(pos, 1);
        pos = message.find('#');
    }
}

void zappy::network::Protocol::printDebug(const std::string &message, std::ostream &stream)
{
    if (_debug)
        stream << message << std::endl;
}
