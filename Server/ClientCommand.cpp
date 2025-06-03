/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#include "ClientCommand.hpp"

std::optional<zappy::server::ClientCommand> zappy::server::getClientCommandFromString(const std::string &str)
{
    std::string cmd = getFirstWord(str);
    for (size_t i = 0; i < clientCommandList.size(); ++i) {
        if (clientCommandList[i] == cmd) {
            return static_cast<ClientCommand>(i);
        }
    }
    return std::nullopt;
}

void zappy::server::handleCommand(ClientCommand cmd) {
    switch (cmd) {
        case ClientCommand::FORWARD:
            handleForward(); break;
        case ClientCommand::RIGHT:
            handleRight(); break;
        case ClientCommand::LEFT:
            handleLeft(); break;
        case ClientCommand::LOOK:
            handleLook(); break;
        case ClientCommand::INVENTORY:
            handleInventory(); break;
        case ClientCommand::BROADCAST:
            handleBroadcast(); break;
        case ClientCommand::CONNECT:
            handleConnectNbr(); break;
        case ClientCommand::FORK:
            handleFork(); break;
        case ClientCommand::EJECT:
            handleEject(); break;
        case ClientCommand::TAKE:
            handleTake(); break;
        case ClientCommand::DROP:
            handleDrop(); break;
        case ClientCommand::INCANTATION:
            handleIncantation(); break;
        default:
            std::cerr << "Unknown command.\n";
    }
}

void zappy::server::processClientInput(const std::string& input)
{
    auto cmd = getClientCommandFromString(input);
    if (cmd.has_value()) {
        handleCommand(*cmd);
    } else {
        std::cerr << "Commande inconnue : " << input << std::endl;
    }
}