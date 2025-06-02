/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#pragma once

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

    }
}