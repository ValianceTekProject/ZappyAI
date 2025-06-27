/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** GuiCommand
*/

#pragma once

#include "TeamsPlayer.hpp"
#include "ServerMap.hpp"

#include <sstream>

namespace zappy {
    namespace game {
        class CommandHandlerGui {
            public:
                CommandHandlerGui(int &freq, int width, int height, int clientNb,
                zappy::game::MapServer &map, std::vector<std::shared_ptr<ITeams>> &teamList)
                :  _teamList(teamList), _freq(freq), _widthMap(width), _heightMap(height),
                  _clientNb(clientNb), _map(map) {};
                ~CommandHandlerGui() = default;
                
                virtual void processClientInput(std::string &input, zappy::game::ServerPlayer &player);

                virtual void initCommandMap();

                std::unordered_map<std::string, std::function<void(ServerPlayer &, const std::string &)>> _commandMapGui;

                std::vector<std::shared_ptr<ITeams>> &_teamList;
                void handleMsz(zappy::game::ServerPlayer &player);
                void handleBct(zappy::game::ServerPlayer &player, const std::string &arg);
                void handleMct(zappy::game::ServerPlayer &player);
                void handleTna(zappy::game::ServerPlayer &player);
                void handlePnw(zappy::game::ServerPlayer &gui);
                void handlePpo(zappy::game::ServerPlayer &player, const std::string &arg);
                void handlePlv(zappy::game::ServerPlayer &player, const std::string &arg);
                void handlePin(zappy::game::ServerPlayer &player, const std::string &arg);
                void handleSgt(zappy::game::ServerPlayer &player);
                void handleSst(zappy::game::ServerPlayer &player, const std::string &arg);

                protected:
                    int &_freq;
                    int _widthMap;
                    int _heightMap;
                    int _clientNb;
                    MapServer &_map;
                    std::unordered_map<std::string,
                        std::function<void(ServerPlayer &, const std::string &)>>
                        _commandMap;
        };
    }
}
