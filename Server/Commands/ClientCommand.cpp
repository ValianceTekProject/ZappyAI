/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#include "ClientCommand.hpp"
#include <algorithm>

zappy::server::CommandHandler::CommandHandler()
{
    this->_commandMap = {
        {"Forward", [this]() { handleForward(); }},
        {"Right", [this]() { handleRight(); }},
        {"Left", [this]() { handleLeft(); }},
        {"Look", [this]() { handleLook(); }},
        {"Inventory", [this]() { handleInventory(); }},
        {"Broadcast", [this]() { handleBroadcast(); }},
        {"Connect_nbr", [this]() { handleConnectNbr(); }},
        {"Fork", [this]() { handleFork(); }},
        {"Eject", [this]() { handleEject(); }},
        {"Take", [this]() { handleTake(); }},
        {"Set", [this]() { handleDrop(); }},
        {"Incantation", [this]() { handleIncantation(); }}
    };
}
std::string zappy::server::CommandHandler::_getFirstWord(
    const std::string &input) const
{
    auto end = std::find_if(input.begin(), input.end(), ::isspace);
    return std::string(input.begin(), end);
}

void zappy::server::CommandHandler::_processClientInput(const std::string& input) {
    auto cmd = this->_getFirstWord(input);
    auto it = this->_commandMap.find(cmd);
    if (it != this->_commandMap.end()) {
        it->second();
        return;
    }
    std::cerr << "Unknown command" << input << std::endl;
}
