/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#include "ClientCommand.hpp"
#include "Game.hpp"
#include "Player.hpp"
#include "Resource.hpp"
#include "ServerPlayer.hpp"
#include <algorithm>
#include <chrono>
#include <mutex>
#include <thread>
#include <unistd.h>

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
}

void zappy::game::CommandHandler::handleRight(
    zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::RIGHT);
    player.lookRight();
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
}

void zappy::game::CommandHandler::handleLeft(zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::LEFT);
    player.lookLeft();
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
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

std::string zappy::game::CommandHandler::_getTileContent(size_t x, size_t y, bool isPlayerTile)
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
            } else {
                if (hasContent) {
                    content += " ";
                }
                content += resourceName;
                hasContent = true;
            }
        }
    }
    
    return content;
}

bool zappy::game::CommandHandler::_checkLastTileInLook(size_t playerLevel, size_t line, int offset)
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

void zappy::game::CommandHandler::handleBroadcast(
    zappy::game::ServerPlayer &player, const std::string &arg)
{
    (void)arg;
    this->_waitCommand(timeLimit::BROADCAST);
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    // implement broadcast;
}

void zappy::game::CommandHandler::handleConnectNbr(
    zappy::game::ServerPlayer &player)
{
    auto playerTeam = dynamic_cast<zappy::game::TeamsPlayer*>(&player.getTeam());
    if (playerTeam) {
        int connectNbr = playerTeam->getClientNb() -
                        playerTeam->getPlayerList().size();
        player.setInAction(false);
        player.getClient().sendMessage(std::to_string(connectNbr) + "\n");
    }
}

void zappy::game::CommandHandler::handleFork(zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::FORK);
    
    auto playerTeam = dynamic_cast<zappy::game::TeamsPlayer*>(&player.getTeam());
    if (playerTeam) {
        playerTeam->allowNewPlayer();
        this->_map.addNewEgg(playerTeam->getTeamId(), player.x, player.y);
        player.setInAction(false);
        player.getClient().sendMessage("ok\n");
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
    });
    commandThread.detach();
}

void zappy::game::CommandHandler::processClientInput(
    const std::string &input, zappy::game::ServerPlayer &player)
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
