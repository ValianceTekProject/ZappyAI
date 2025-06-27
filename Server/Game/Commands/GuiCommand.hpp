/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** GuiCommand
*/

#pragma once

#include "ClientCommand.hpp"
#include "TeamsPlayer.hpp"

#include <sstream>

namespace zappy {
    namespace game {
        class CommandHandlerGui : public CommandHandler {
            public:
                CommandHandlerGui(int &freq, int width, int height, int clientNb, zappy::game::MapServer &map, std::vector<std::shared_ptr<ITeams>> &teamList) : CommandHandler(freq, width, height, clientNb, map, teamList), _teamList(teamList) {};
                ~CommandHandlerGui() = default;
                
                void processClientInput(std::string &input, zappy::game::ServerPlayer &player) override;

                void initCommandMap() override;

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
        };
    }
}
