/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#include "ClientCommand.hpp"
#include "Game.hpp"
#include "GameError.hpp"
#include "Player.hpp"
#include "Resource.hpp"
#include "ServerPlayer.hpp"
#include <algorithm>
#include <chrono>
#include <memory>
#include <mutex>
#include <thread>
#include <unistd.h>

void zappy::game::CommandHandler::messageToGUI(const std::string &msg)
{
    for (auto &team : _teamList) {
        if (team->getName() == "GRAPHIC") {
            for (auto &player : team->getPlayerList()) {
                if (player)
                    player->getClient().sendMessage(msg);
            }
        }
    }
}

void zappy::game::CommandHandler::initCommandMap()
{
    this->_commandMap = {
        {"Forward",
            [this](ServerPlayer &player, const std::string &) {
                handleForward(player);
            }},
        {"Right",
            [this](ServerPlayer &player, const std::string &) {
                handleRight(player);
            }},
        {"Left",
            [this](ServerPlayer &player, const std::string &) {
                handleLeft(player);
            }},
        {"Look",
            [this](ServerPlayer &player, const std::string &) {
                handleLook(player);
            }},
        {"Inventory",
            [this](ServerPlayer &player, const std::string &) {
                handleInventory(player);
            }},
        {"Broadcast",
            [this](ServerPlayer &player, const std::string &arg) {
                handleBroadcast(player, arg);
            }},
        {"Connect_nbr",
            [this](ServerPlayer &player, const std::string &) {
                handleConnectNbr(player);
            }},
        {"Fork",
            [this](ServerPlayer &player, const std::string &) {
                handleFork(player);
            }},
        {"Eject",
            [this](ServerPlayer &player, const std::string &) {
                handleEject(player);
            }},
        {"Take",
            [this](ServerPlayer &player, const std::string &arg) {
                handleTake(player, arg);
            }},
        {"Set",
            [this](ServerPlayer &player, const std::string &arg) {
                handleDrop(player, arg);
            }},
        {"Incantation", [this](ServerPlayer &player, const std::string &) {
             handleIncantation(player);
         }}};
}

void zappy::game::CommandHandler::_waitCommand(timeLimit limit)
{
    auto commandTime = static_cast<double>(limit) / this->_freq;
    auto timeNeeded = std::chrono::duration<double>(commandTime);
    std::this_thread::sleep_for(std::chrono::duration<double>(timeNeeded));
}

void zappy::game::CommandHandler::handleForward(
    zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::FORWARD);
    player.stepForward(this->_widthMap, this->_heightMap);
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    std::string msg = "ppo #" + std::to_string(player.getId()) + " " + 
        std::to_string(player.x) + " " + 
        std::to_string(player.y) + " " + 
        std::to_string(static_cast<int>(player.orientation + 1)) + "\n";
    this->messageToGUI(msg);
}

void zappy::game::CommandHandler::handleRight(
    zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::RIGHT);
    player.lookRight();
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    std::string msg = "ppo #" + std::to_string(player.getId()) + " " + 
        std::to_string(player.x) + " " + 
        std::to_string(player.y) + " " + 
        std::to_string(static_cast<int>(player.orientation + 1)) + "\n";
    this->messageToGUI(msg);
}

void zappy::game::CommandHandler::handleLeft(zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::LEFT);
    player.lookLeft();
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    std::string msg = "ppo #" + std::to_string(player.getId()) + " " + 
        std::to_string(player.x) + " " + 
        std::to_string(player.y) + " " + 
        std::to_string(static_cast<int>(player.orientation + 1)) + "\n";
    this->messageToGUI(msg);
}

std::pair<size_t, size_t> zappy::game::CommandHandler::_normalizeCoords(
    size_t x, size_t y)
{
    x = ((x % this->_widthMap) + this->_widthMap) % this->_widthMap;
    y = ((y % this->_heightMap) + this->_heightMap) % this->_heightMap;
    return {static_cast<size_t>(x), static_cast<size_t>(y)};
}

void zappy::game::CommandHandler::_getDirectionVector(
    const Player &player, int &dx, int &dy)
{
    Orientation orientation = player.orientation;

    switch (orientation) {
        case Orientation::NORTH:
            dx = 0;
            dy = -1;
            break;
        case Orientation::EAST:
            dx = 1;
            dy = 0;
            break;
        case Orientation::SOUTH:
            dx = 0;
            dy = 1;
            break;
        case Orientation::WEST:
            dx = -1;
            dy = 0;
            break;
    }
}

std::pair<int, int> zappy::game::CommandHandler::_computeLookTarget(
    zappy::game::ServerPlayer &player, size_t line, int offset)
{
    Orientation orientation = player.orientation;
    size_t playerX = player.x;
    size_t playerY = player.y;
    int dx = 0;
    int dy = 0;

    this->_getDirectionVector(player, dx, dy);

    int targetX =
        static_cast<int>(playerX) + dx * static_cast<int>(line) +
        (orientation == Orientation::NORTH || orientation == Orientation::SOUTH
                ? offset
                : (dy * offset));

    int targetY =
        static_cast<int>(playerY) + dy * static_cast<int>(line) +
        (orientation == Orientation::EAST || orientation == Orientation::WEST
                ? offset
                : (-dx * offset));

    return {targetX, targetY};
}

std::string zappy::game::CommandHandler::_getTileContent(
    size_t x, size_t y, bool isPlayerTile)
{
    std::string content = "";
    auto &tile = this->_map.getTile(x, y);
    bool hasContent = false;

    for (const auto &resourceName : names) {
        zappy::game::Resource resource = getResource(resourceName);
        size_t quantity = tile.getResourceQuantity(resource);

        for (size_t i = 0; i < quantity; ++i) {
            if (isPlayerTile) {
                content += " " + resourceName;
                continue;
            }
            if (hasContent)
                content += " ";
            content += resourceName;
            hasContent = true;
        }
    }

    return content;
}

bool zappy::game::CommandHandler::_checkLastTileInLook(
    size_t playerLevel, size_t line, int offset)
{
    return (line == playerLevel && offset == static_cast<int>(line));
}

std::string zappy::game::CommandHandler::_lookLine(
    zappy::game::ServerPlayer &player, size_t line)
{
    std::string lineMsg = "";

    for (int offset = static_cast<int>(line) * -1;
        offset <= static_cast<int>(line); offset += 1) {
        auto [targetX, targetY] =
            this->_computeLookTarget(player, line, offset);
        auto [normalizedX, normalizedY] =
            this->_normalizeCoords(targetX, targetY);

        std::string tileContent = this->_getTileContent(
            normalizedX, normalizedY, line == 0 && offset == 0);
        lineMsg += tileContent;

        if (!this->_checkLastTileInLook(player.level, line, offset))
            lineMsg += ",";
    }

    return lineMsg;
}

std::string zappy::game::CommandHandler::_buildLookMessage(
    zappy::game::ServerPlayer &player)
{
    std::string msg = "[player";
    size_t playerLevel = player.level;

    for (size_t line = 0; line <= playerLevel; line += 1) {
        std::string lineMsg = this->_lookLine(player, line);
        msg += lineMsg;
    }

    msg += "]\n";
    return msg;
}

void zappy::game::CommandHandler::handleLook(zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::LOOK);
    std::string msg = this->_buildLookMessage(player);

    player.setInAction(false);
    player.getClient().sendMessage(msg);
}

void zappy::game::CommandHandler::handleInventory(
    zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::INVENTORY);
    zappy::game::Inventory playerInv = player.getInventory();
    std::string msg = "[";
    for (auto foodName : names)
        msg += foodName + " " +
               std::to_string(
                   playerInv.getResourceQuantity(getResource(foodName))) +
               ",";
    msg.pop_back();
    msg += "]\n";
    player.setInAction(false);
    player.getClient().sendMessage(msg);
}

std::pair<int, int> zappy::game::CommandHandler::_computeBroadcastDistance(
    int x1, int y1, int x2, int y2)
{
    int dx = x2 - x1;
    int dx_round = 0;
    if (dx > 0)
        dx_round = dx - static_cast<int>(this->_widthMap);
    else
        dx_round = dx + static_cast<int>(this->_widthMap);
    if (std::abs(dx_round) < std::abs(dx))
        dx = dx_round;

    int dy = y2 - y1;
    int dy_round = 0;
    if (dy > 0)
        dy_round = dy - static_cast<int>(this->_heightMap);
    else
        dy_round = dy + static_cast<int>(this->_heightMap);
    if (std::abs(dy_round) < std::abs(dy))
        dy = dy_round;

    return {dx, dy};
}

int zappy::game::CommandHandler::_getSoundCardinalPoint(
    int relativeX, int relativeY)
{
    if (relativeY < 0) {
        if (relativeX < 0)
            return static_cast<int>(SoundDirection::NORTHWEST);
        else if (relativeX > 0)
            return static_cast<int>(SoundDirection::NORTHEAST);
        else
            return static_cast<int>(SoundDirection::NORTH);
    } else if (relativeY > 0) {
        if (relativeX < 0)
            return static_cast<int>(SoundDirection::SOUTHWEST);
        else if (relativeX > 0)
            return static_cast<int>(SoundDirection::SOUTHEAST);
        else
            return static_cast<int>(SoundDirection::SOUTH);
    } else {
        if (relativeX < 0)
            return static_cast<int>(SoundDirection::WEST);
    }
    return static_cast<int>(SoundDirection::EAST);
}

int zappy::game::CommandHandler::_computeSoundDirection(
    const ServerPlayer &player, const ServerPlayer &receiver)
{
    if (player.x == receiver.x && player.y == receiver.y)
        return static_cast<int>(SoundDirection::SAME_POSITION);

    auto [dx, dy] = this->_computeBroadcastDistance(
        static_cast<int>(receiver.x), static_cast<int>(receiver.y),
        static_cast<int>(player.x), static_cast<int>(player.y));

    int relativeX = 0;
    int relativeY = 0;

    switch (receiver.orientation) {
        case Orientation::NORTH:
            relativeX = dx;
            relativeY = dy;
            break;
        case Orientation::EAST:
            relativeX = -dy;
            relativeY = dx;
            break;
        case Orientation::SOUTH:
            relativeX = -dx;
            relativeY = -dy;
            break;
        case Orientation::WEST:
            relativeX = dy;
            relativeY = -dx;
            break;
    }
    return this->_getSoundCardinalPoint(relativeX, relativeY);
}

void zappy::game::CommandHandler::handleBroadcast(
    zappy::game::ServerPlayer &player, const std::string &arg)
{
    this->_waitCommand(timeLimit::BROADCAST);

    for (auto &team : this->_teamList) {
        for (auto &teamPlayer : team->getPlayerList()) {
            std::cout << "PlayerPos: " << teamPlayer->x << " " << teamPlayer->y
                      << std::endl;
            if (teamPlayer->getClient().getSocket() !=
                player.getClient().getSocket()) {
                int direction =
                    this->_computeSoundDirection(player, *teamPlayer);
                std::string broadcastMsg =
                    "message " + std::to_string(direction) + ", " + arg + "\n";
                teamPlayer->getClient().sendMessage(broadcastMsg);
            }
        }
    }
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    this->messageToGUI(std::string(
        "pbc #" + std::to_string(player.getId()) + " " + arg + "\n"));
}

void zappy::game::CommandHandler::handleConnectNbr(
    zappy::game::ServerPlayer &player)
{
    auto playerTeam =
        dynamic_cast<zappy::game::TeamsPlayer *>(&player.getTeam());
    if (playerTeam) {
        int connectNbr =
            playerTeam->getClientNb() - playerTeam->getPlayerList().size();
        player.setInAction(false);
        player.getClient().sendMessage(std::to_string(connectNbr) + "\n");
    }
}

void zappy::game::CommandHandler::handleFork(zappy::game::ServerPlayer &player)
{
    this->messageToGUI("pfk #" + std::to_string(player.getId()) + "\n");
    this->_waitCommand(timeLimit::FORK);

    auto playerTeam =
        dynamic_cast<zappy::game::TeamsPlayer *>(&player.getTeam());
    if (playerTeam) {
        playerTeam->allowNewPlayer();
        this->_map.addNewEgg(playerTeam->getTeamId(), player.x, player.y);
        player.setInAction(false);
        player.getClient().sendMessage("ok\n");
        this->messageToGUI("enw #" + std::to_string(player.getTeam().getTeamId()) + " #" +
            std::to_string(player.getId()) + " " +
            std::to_string(player.x) + " " +
            std::to_string(player.y) + "\n");
    }
}

void zappy::game::CommandHandler::handleTake(
    zappy::game::ServerPlayer &player, const std::string &arg)
{
    this->_waitCommand(timeLimit::TAKE);
    auto objectTake = std::find_if(names.begin(), names.end(),
        [&arg](const std::string &name) { return name == arg; });

    if (objectTake == names.end())
        return player.getClient().sendMessage("ko\n");

    std::lock_guard<std::mutex> lock(this->_resourceMutex);
    zappy::game::Resource resource = getResource(arg);

    auto &tile = this->_map.getTile(player.x, player.y);
    if (tile.getResourceQuantity(resource) == 0)
        return player.getClient().sendMessage("ko\n");

    player.collectRessource(resource);
    tile.removeResource(resource);
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    this->messageToGUI("pgt #" +
        std::to_string(player.getId()) +
        " " + std::to_string(castResource(resource)) +
        "\n");
    for (auto &team : this->_teamList) {
        if (team->getName() == "GRAPHIC") {
            for (auto &players : team->getPlayerList()) {
                handlePin(*players, std::to_string(player.getId()));
                handleBct(*players, std::string(std::to_string(player.x)) +
                    " " + std::string(std::to_string(player.x)));
            }
        }
    }
}

void zappy::game::CommandHandler::handleDrop(
    zappy::game::ServerPlayer &player, const std::string &arg)
{
    this->_waitCommand(timeLimit::SET);
    auto objectDrop = std::find_if(names.begin(), names.end(),
        [&arg](const std::string &name) { return name == arg; });

    if (objectDrop == names.end())
        return player.getClient().sendMessage("ko\n");

    std::lock_guard<std::mutex> lock(this->_resourceMutex);
    zappy::game::Resource resource = getResource(arg);

    auto &inventory = player.getInventory();
    if (inventory.getResourceQuantity(resource) == 0)
        return player.getClient().sendMessage("ko\n");

    this->_map.getTile(player.x, player.y).addSingleResource(resource);
    player.dropRessource(resource);
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    this->messageToGUI("pdr #" + std::to_string(player.getId()) + " " +
        std::to_string(castResource(resource)) + "\n");
    for (auto &team : this->_teamList) {
        if (team->getName() == "GRAPHIC") {
            for (auto &players : team->getPlayerList()) {
                handlePin(*players, std::to_string(player.getId()));
                handleBct(*players, std::string(std::to_string(player.x)) +
                    " " + std::string(std::to_string(player.x)));
            }
        }
    }
}

std::vector<std::weak_ptr<zappy::game::ServerPlayer>>
zappy::game::CommandHandler::_getPlayersOnTile(int x, int y, size_t level)
{
    std::vector<std::weak_ptr<ServerPlayer>> players;

    for (auto &team : this->_teamList) {
        for (auto &player : team->getPlayerList()) {
            if (player->x == x && player->y == y && player->level == level &&
                !player->isInAction()) {
                players.push_back(player);
            }
        }
    }
    return players;
}

bool zappy::game::CommandHandler::_checkIncantationResources(
    size_t x, size_t y, size_t level)
{
    if (level < minLevel || level >= maxLevel)
        return false;

    auto &tile = this->_map.getTile(x, y);
    const auto &requirements = elevationRequirements[level - 1];

    return tile.getResourceQuantity(Resource::LINEMATE) >=
               requirements.linemate &&
           tile.getResourceQuantity(Resource::DERAUMERE) >=
               requirements.deraumere &&
           tile.getResourceQuantity(Resource::SIBUR) >= requirements.sibur &&
           tile.getResourceQuantity(Resource::MENDIANE) >=
               requirements.mendiane &&
           tile.getResourceQuantity(Resource::PHIRAS) >= requirements.phiras &&
           tile.getResourceQuantity(Resource::THYSTAME) >=
               requirements.thystame;
}

bool zappy::game::CommandHandler::_checkIncantationConditions(
    const zappy::game::ServerPlayer &player)
{
    const auto &requirements = elevationRequirements[player.level - 1];

    if (player.level >= maxLevel)
        return false;
    auto players = this->_getPlayersOnTile(player.x, player.y, player.level);

    if (players.size() < requirements.players) {
        return false;
    }
    return this->_checkIncantationResources(player.x, player.y, player.level);
}

void zappy::game::CommandHandler::_consumeElevationResources(
    size_t x, size_t y, size_t level)
{
    std::lock_guard<std::mutex> lock(this->_resourceMutex);
    auto &tile = this->_map.getTile(x, y);
    const auto &req = elevationRequirements[level - 1];

    for (size_t i = 0; i < req.linemate; i += 1)
        tile.removeResource(Resource::LINEMATE);
    for (size_t i = 0; i < req.deraumere; i += 1)
        tile.removeResource(Resource::DERAUMERE);
    for (size_t i = 0; i < req.sibur; i += 1)
        tile.removeResource(Resource::SIBUR);
    for (size_t i = 0; i < req.mendiane; i += 1)
        tile.removeResource(Resource::MENDIANE);
    for (size_t i = 0; i < req.phiras; i += 1)
        tile.removeResource(Resource::PHIRAS);
    for (size_t i = 0; i < req.thystame; i += 1)
        tile.removeResource(Resource::THYSTAME);
}

void zappy::game::CommandHandler::_setPrayer(zappy::game::ServerPlayer &player)
{
    auto playersOnTile =
        this->_getPlayersOnTile(player.x, player.y, player.level);
    std::for_each(playersOnTile.begin(), playersOnTile.end(),
        [](std::weak_ptr<ServerPlayer> playerOnTile) {
            auto sharedPlayer = playerOnTile.lock();
            if (!sharedPlayer)
                throw GameError("Unable to lock weak ptr", "Allowing praying");
            if (sharedPlayer->isInAction())
                return;
            sharedPlayer->setInAction(true);
            sharedPlayer->pray();
            sharedPlayer->getClient().sendMessage("Elevation underway\n");
        });
}

void zappy::game::CommandHandler::_elevatePlayer(
    zappy::game::ServerPlayer &player)
{
    auto playersOnTile =
        this->_getPlayersOnTile(player.x, player.y, player.level);
    std::for_each(playersOnTile.begin(), playersOnTile.end(),
        [](std::weak_ptr<ServerPlayer> playerOnTile) {
            auto sharedPlayer = playerOnTile.lock();
            if (!sharedPlayer)
                throw GameError("Unable to lock weak ptr", "Elevation");
            if (!sharedPlayer->isPraying())
                return;
            sharedPlayer->level += 1;
            sharedPlayer->stopPraying();
            sharedPlayer->setInAction(false);
            sharedPlayer->getClient().sendMessage(
                std::string("Current level:") +
                std::to_string(sharedPlayer->level) + "\n");
        });
    this->messageToGUI(std::string("pie " +
                std::to_string(player.x) + " " +
                std::to_string(player.y) + " 1\n"));
}

void zappy::game::CommandHandler::handleIncantation(
    zappy::game::ServerPlayer &player)
{
    if (!this->_checkIncantationConditions(player)) {
        this->messageToGUI(std::string("pie " +
                std::to_string(player.x) + " " +
                std::to_string(player.y) + " 0\n"));
        return player.getClient().sendMessage("ko\n");
    }
    this->_setPrayer(player);
    std::string guiMsg = "pic " + std::to_string(player.x) + " " +
                         std::to_string(player.y) + " " +
                         std::to_string(player.level);
    auto otherPlayers =
        this->_getPlayersOnTile(player.x, player.y, player.level);

    std::for_each(otherPlayers.begin(), otherPlayers.end(),
        [&guiMsg](std::weak_ptr<ServerPlayer> player) {
            auto sharedPlayer = player.lock();
            if (!sharedPlayer->isPraying())
                return;
            guiMsg += " #";
            guiMsg += sharedPlayer->getId();
        });
    guiMsg += "\n";
    this->messageToGUI(guiMsg);
    this->_waitCommand(timeLimit::INCANTATION);

    if (!this->_checkIncantationConditions(player)) {
        this->messageToGUI(std::string("pie " +
                std::to_string(player.x) + " " +
                std::to_string(player.y) + " 0\n"));
        return player.getClient().sendMessage("ko\n");
    }
    this->_consumeElevationResources(player.x, player.y, player.level);
    this->_elevatePlayer(player);
    player.setInAction(false);
}

void zappy::game::CommandHandler::_executeCommand(
    zappy::game::ServerPlayer &player,
    std::function<void(ServerPlayer &, const std::string &)> function,
    const std::string &args)
{
    std::thread commandThread([&player, function, args]() {
        if (player.isInAction())
            return;

        player.setInAction(true);
        player.startChrono();

        player.getClient().queueMessage.pop();
        function(player, args);
        player.setInAction(false);
    });
    commandThread.detach();
}

void zappy::game::CommandHandler::processClientInput(
    std::string &input, zappy::game::ServerPlayer &player)
{
    if (this->_commandMap.empty())
        this->initCommandMap();

    auto spacePos = input.find(' ');
    std::string cmd = input.substr(0, spacePos);
    std::string args =
        (spacePos != std::string::npos) ? input.substr(spacePos + 1) : "";

    if (!args.empty() && args.back() == '\n')
        args.pop_back();

    auto it = this->_commandMap.find(cmd);
    if (it != this->_commandMap.end())
        return this->_executeCommand(player, it->second, args);
    if (player.isInAction() == false) {
        player.getClient().queueMessage.pop();
        player.getClient().sendMessage("ko\n");
    }
}
