/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#include <algorithm>
#include "ClientCommand.hpp"
#include "Game.hpp"

void zappy::game::CommandHandler::initCommandMap()
{
    this->_commandMap = {
        {"Forward", [this](ServerPlayer &player, const std::string &) { handleForward(player); }},
        {"Right", [this](ServerPlayer &player, const std::string &) { handleRight(player); }},
        {"Left", [this](ServerPlayer &player, const std::string &) { handleLeft(player); }},
        {"Look", [this](ServerPlayer &player, const std::string &) { handleLook(player); }},
        {"Inventory", [this](ServerPlayer &player, const std::string &) { handleInventory(player); }},
        {"Broadcast", [this](ServerPlayer &player, const std::string &arg) { handleBroadcast(player, arg); }},
        {"Connect_nbr", [this](ServerPlayer &player, const std::string &) { handleConnectNbr(player); }},
        {"Fork", [this](ServerPlayer &player, const std::string &) { handleFork(player); }},
        {"Eject", [this](ServerPlayer &player, const std::string &) { handleEject(player); }},
        {"Take", [this](ServerPlayer &player, const std::string &arg) { handleTake(player, arg); }},
        {"Set", [this](ServerPlayer &player, const std::string &arg) { handleDrop(player, arg); }},
        {"Incantation", [this](ServerPlayer &player, const std::string &) { handleIncantation(player); }}
    };
}

void zappy::game::CommandHandler::handleForward(zappy::game::ServerPlayer &player)
{
    if (!player.getChonoStart()) {
        player.stepForward(this->_widthMap, this->_heightMap);
        player.startChrono();
        player.setChronoStart(true);
        player.getClient().sendMessage("ok\n");
        return;
    }

    double seconds = static_cast<double>(static_cast<int>(timeLimit::FORWARD)) / this->_freq;
    auto timeNeed = std::chrono::duration<double>(seconds);
    if (player.getChrono() >= timeNeed) {
        player.stepForward(this->_widthMap, this->_heightMap);
        player.startChrono();
        player.getClient().sendMessage("ok\n");
    } else
        player.getClient().sendMessage("ko\n");

}

void zappy::game::CommandHandler::handleRight(zappy::game::ServerPlayer &player)
{
    if (!player.getChonoStart()) {
        player.lookRight();
        player.startChrono();
        player.setChronoStart(true);
        player.getClient().sendMessage("ok\n");
        return;
    }

    double seconds = static_cast<double>(static_cast<int>(timeLimit::RIGHT)) / this->_freq;
    auto timeNeed = std::chrono::duration<double>(seconds);
    if (player.getChrono() >= timeNeed) {
        player.lookRight();
        player.startChrono();
        player.getClient().sendMessage("ok\n");
    } else
        player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandler::handleLeft(zappy::game::ServerPlayer &player)
{
    if (!player.getChonoStart()) {
        player.lookLeft();
        player.startChrono();
        player.setChronoStart(true);
        player.getClient().sendMessage("ok\n");
        return;
    }

    double seconds = static_cast<double>(static_cast<int>(timeLimit::LEFT)) / this->_freq;
    auto timeNeed = std::chrono::duration<double>(seconds);
    if (player.getChrono() >= timeNeed) {
        player.lookLeft();
        player.startChrono();
        player.getClient().sendMessage("ok\n");
    } else
        player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandler::handleInventory(zappy::game::ServerPlayer &player)
{
    if (!player.getChonoStart()) {
        zappy::game::Inventory playerInv = player.getInventory();
        std::string msg = "[";
        for (auto foodName : names)
            msg += foodName + " " + std::to_string(playerInv.getResourceQuantity(getResource(foodName))) + ",";
        msg.pop_back();
        msg += "]\n";
        player.getClient().sendMessage(msg);
        player.startChrono();
        player.setChronoStart(true);
        return;
    }

    double seconds = static_cast<double>(static_cast<int>(timeLimit::INVENTORY)) / this->_freq;
    auto timeNeed = std::chrono::duration<double>(seconds);
    if (player.getChrono() >= timeNeed) {
        zappy::game::Inventory playerInv = player.getInventory();
        std::string msg = "[";
        for (auto foodName : names)
            msg += foodName + " " + std::to_string(playerInv.getResourceQuantity(getResource(foodName))) + ",";
        msg.pop_back();
        msg += "]\n";
        player.getClient().sendMessage(msg);
        player.lookLeft();
        player.startChrono();
    } else
        player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandler::handleBroadcast(zappy::game::ServerPlayer &player, const std::string &arg)
{
    (void)arg;
    if (!player.getChonoStart()) {
        player.startChrono();
        player.setChronoStart(true);
        player.getClient().sendMessage("ok\n");
        return;
    }

    double seconds = static_cast<double>(static_cast<int>(timeLimit::BROADCAST)) / this->_freq;
    auto timeNeed = std::chrono::duration<double>(seconds);
    if (player.getChrono() >= timeNeed) {
        player.startChrono();
        player.getClient().sendMessage("ok\n");
    } else
        player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandler::handleConnectNbr(zappy::game::ServerPlayer &player)
{
    int connectNbr = player.getTeam().getClientNb() - player.getTeam().getPlayerList().size();
    player.getClient().sendMessage(std::to_string(connectNbr) + "\n");
    player.startChrono();
    player.setChronoStart(true);
    return;
}

void zappy::game::CommandHandler::handleFork(zappy::game::ServerPlayer &player)
{
    if (!player.getChonoStart()) {
        player.startChrono();
        player.setChronoStart(true);
        player.getClient().sendMessage("ok\n");
        return;
    }

    if (player.getChrono() >= static_cast<std::chrono::seconds>(static_cast<int>(timeLimit::FORK) / this->_freq)) {
        player.startChrono();
        player.getClient().sendMessage("ok\n");
    } else 
        player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandler::handleTake(zappy::game::ServerPlayer &player, const std::string &arg)
{
    (void)arg;
    if (!player.getChonoStart()) {
        player.startChrono();
        player.setChronoStart(true);
        player.getClient().sendMessage("ok\n");
        return;
    }

    if (player.getChrono() >= static_cast<std::chrono::seconds>(static_cast<int>(timeLimit::TAKE) / this->_freq)) {
        player.startChrono();
        player.getClient().sendMessage("ok\n");
    } else 
        player.getClient().sendMessage("ko\n");
}

std::string zappy::game::CommandHandler::_getFirstWord(
    const std::string &input) const
{
    auto end = std::find_if(input.begin(), input.end(), ::isspace);
    return std::string(input.begin(), end);
}

void zappy::game::CommandHandler::processClientInput(const std::string &input, zappy::game::ServerPlayer &player)
{
    if (this->_commandMap.empty())
        this->initCommandMap();

    auto spacePos = input.find(' ');
    std::string cmd = input.substr(0, spacePos);
    std::string args = (spacePos != std::string::npos) ? input.substr(spacePos + 1) : "";

    if (!args.empty() && args.back() == '\n')
        args.pop_back();

    auto it = this->_commandMap.find(cmd);
    if (it != this->_commandMap.end()) {
        it->second(player, args);
    } else
        player.getClient().sendMessage("ko\n");
}

