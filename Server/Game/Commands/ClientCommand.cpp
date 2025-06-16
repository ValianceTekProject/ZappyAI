/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#include <algorithm>
#include "ClientCommand.hpp"
#include "Game.hpp"

void zappy::game::CommandHandler::initCommandMap(zappy::game::ServerPlayer &player)
{
    this->_commandMap = {
        {"Forward", [this, &player]() { handleForward(player); }},
        {"Right", [this, &player]() { handleRight(player); }},
        {"Left", [this, &player]() { handleLeft(player); }},
        {"Look", [this, &player]() { handleLook(player); }},
        {"Inventory", [this, &player]() { handleInventory(player); }},
        {"Broadcast", [this, &player]() { handleBroadcast(player); }},
        {"Connect_nbr", [this, &player]() { handleConnectNbr(player); }},
        {"Fork", [this, &player]() { handleFork(player); }},
        {"Eject", [this, &player]() { handleEject(player); }},
        {"Take", [this, &player]() { handleTake(player); }},
        {"Set", [this, &player]() { handleDrop(player); }},
        {"Incantation", [this, &player]() { handleIncantation(player); }}
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

void zappy::game::CommandHandler::handleBroadcast(zappy::game::ServerPlayer &player)
{
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

void zappy::game::CommandHandler::handleFork(zappy::game::ServerPlayer &player)
{
    if (!player.getChonoStart()) {
        player.startChrono();
        player.setChronoStart(true);
        player.getClient().sendMessage("ok\n");
        return;
    }

    if (player.getChrono() >= static_cast<std::chrono::seconds>(static_cast<int>(timeLimit::FORWARD) / this->_freq)) {
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

void zappy::game::CommandHandler::processClientInput(const std::string& input, zappy::game::ServerPlayer &player)
{
    this->initCommandMap(player);
    auto cmd = this->_getFirstWord(input);
    auto it = this->_commandMap.find(cmd);
    if (it != this->_commandMap.end()) {
        it->second();
        return;
    }
    std::cout << static_cast<int>(player.getClient().getState()) << std::endl;
    player.getClient().sendMessage("ko\n");
}
