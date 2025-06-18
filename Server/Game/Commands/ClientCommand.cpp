/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#include "ClientCommand.hpp"
#include "Game.hpp"
#include "Resource.hpp"
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
    int connectNbr = player.getTeam().getClientNb() -
                     player.getTeam().getPlayerList().size();
    player.setInAction(false);
    player.getClient().sendMessage(std::to_string(connectNbr) + "\n");
}

void zappy::game::CommandHandler::handleFork(zappy::game::ServerPlayer &player)
{
    this->_waitCommand(timeLimit::FORK);
    player.setInAction(false);
    player.getClient().sendMessage("ok\n");
    // implement fork;
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
            return player.getClient().sendMessage("ko\n");

        player.setInAction(true);
        player.startChrono();

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
    player.getClient().sendMessage("ko\n");
}
