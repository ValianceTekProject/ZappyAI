/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#pragma once

#include <optional>
#include <string>
#include <iostream>
#include <algorithm>
#include <cctype>

#include "Server.hpp"

namespace zappy {
    namespace server {
        enum class ClientCommand {
            FORWARD,
            RIGHT,
            LEFT,
            LOOK,
            INVENTORY,
            BROADCAST,
            CONNECT,
            FORK,
            EJECT,
            TAKE,
            DROP,
            INCANTATION,
            COUNT
        };

        std::string getFirstWord(const std::string& str) {
            auto end = std::find_if(str.begin(), str.end(), ::isspace);
            return std::string(str.begin(), end);
        }

        std::optional<ClientCommand> getClientCommandFromString(const std::string& str);

        static constexpr size_t castClientCommand(ClientCommand cmd) noexcept {
            return static_cast<size_t>(cmd);
        }

        const std::array<std::string, castClientCommand(ClientCommand::COUNT)> clientCommandList = {
            "Forward",
            "Right",
            "Left",
            "Look",
            "Inventory",
            "Broadcast",
            "Connect_nbr",
            "Fork",
            "Eject",
            "Take",
            "Set",
            "Incantation"
        };
        void handleForward()      { std::cout << "Forward\n"; }
        void handleRight()        { std::cout << "Right\n"; }
        void handleLeft()         { std::cout << "Left\n"; }
        void handleLook()         { std::cout << "Look\n"; }
        void handleInventory()    { std::cout << "Inventory\n"; }
        void handleBroadcast()    { std::cout << "Broadcast\n"; }
        void handleConnectNbr()   { std::cout << "Connect_nbr\n"; }
        void handleFork()         { std::cout << "Fork\n"; }
        void handleEject()        { std::cout << "Eject\n"; }
        void handleTake()         { std::cout << "Take\n"; }
        void handleDrop()         { std::cout << "Set (Drop)\n"; }
        void handleIncantation()  { std::cout << "Incantation\n"; }

        void handleCommand(ClientCommand cmd);

        void processClientInput(const std::string& input);

    } 

}