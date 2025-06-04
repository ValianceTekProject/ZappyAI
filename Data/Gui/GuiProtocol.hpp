/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GuiProtocol.hpp
*/

#pragma once

#include <iostream>
#include <map>
#include <algorithm>

namespace zappy {
    namespace network {
        enum class GuiProtocol {
            MAP_SIZE,               // msz
            TILE_CONTENT,           // bct
            TEAM_NAME,              // tna
            NEW_PLAYER,             // pnw
            PLAYER_POSITION,        // ppo
            PLAYER_LEVEL,           // plv
            PLAYER_INVENTORY,       // pin
            PLAYER_EXPULSION,       // pex
            PLAYER_BROADCAST,       // pbc
            INCANTATION_START,      // pic
            INCANTATION_END,        // pie
            EGG_LAYING,             // pfk
            RESOURCE_DROP,          // pdr
            RESOURCE_COLLECT,       // pgt
            PLAYER_DEATH,           // pdi
            EGG_CREATED,            // enw
            EGG_HATCH,              // ebo
            EGG_DESTROYED,          // edi
            TIME_UNIT_REQUEST,      // sgt
            TIME_UNIT_MODIFICATION, // sst
            GAME_END,               // seg
            SERVER_MESSAGE,         // smg
            UNKNOWN_COMMAND,        // suc
            COMMAND_PARAMETER,      // sbp
            SIZE
        };

        using GP = GuiProtocol;

        // Convertit un enum en index
        static constexpr size_t castGuiProtocol(GP cmd) noexcept {
            return static_cast<size_t>(cmd);
        }

        static constexpr size_t GuiProtocolCount = castGuiProtocol(GP::SIZE);

        const std::map<std::string, GuiProtocol> guiProtocolMap = {
            { "msz", GP::MAP_SIZE },
            { "bct", GP::TILE_CONTENT },
            { "tna", GP::TEAM_NAME },
            { "pnw", GP::NEW_PLAYER },
            { "ppo", GP::PLAYER_POSITION },
            { "plv", GP::PLAYER_LEVEL },
            { "pin", GP::PLAYER_INVENTORY },
            { "pex", GP::PLAYER_EXPULSION },
            { "pbc", GP::PLAYER_BROADCAST },
            { "pic", GP::INCANTATION_START },
            { "pie", GP::INCANTATION_END },
            { "pfk", GP::EGG_LAYING },
            { "pdr", GP::RESOURCE_DROP },
            { "pgt", GP::RESOURCE_COLLECT },
            { "pdi", GP::PLAYER_DEATH },
            { "enw", GP::EGG_CREATED },
            { "ebo", GP::EGG_HATCH },
            { "edi", GP::EGG_DESTROYED },
            { "sgt", GP::TIME_UNIT_REQUEST },
            { "sst", GP::TIME_UNIT_MODIFICATION },
            { "seg", GP::GAME_END },
            { "smg", GP::SERVER_MESSAGE },
            { "suc", GP::UNKNOWN_COMMAND },
            { "sbp", GP::COMMAND_PARAMETER }
        };

        inline GuiProtocol getGuiProtocol(const std::string &str) {
            auto it = guiProtocolMap.find(str);
            if (it == guiProtocolMap.end())
                return GP::UNKNOWN_COMMAND;
            return it->second;
        }
    }
}
