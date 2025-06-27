/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#pragma once

#include "ServerMap.hpp"
#include "ServerPlayer.hpp"
#include "ITeams.hpp"
#include <functional>
#include <iostream>
#include <map>
#include <string>
#include "GuiCommand.hpp"

namespace zappy {
    namespace game {
        constexpr int minLevel = 1;
        constexpr int maxLevel = 8;

        typedef struct elevation_s {
            size_t players;
            size_t linemate;
            size_t deraumere;
            size_t sibur;
            size_t mendiane;
            size_t phiras;
            size_t thystame;
        } elevation_t;

        const std::array<elevation_t, 7> elevationRequirements = {{
            {1, 1, 0, 0, 0, 0, 0}, {2, 1, 1, 1, 0, 0, 0},
            {2, 2, 0, 1, 0, 2, 0}, {4, 1, 1, 2, 0, 1, 0},
            {4, 1, 2, 1, 3, 0, 0}, {6, 1, 2, 3, 0, 1, 0},
            {6, 2, 2, 2, 2, 2, 1}}};

        class CommandHandler : public CommandHandlerGui {
           public:
            enum class timeLimit {
                FORWARD = 7,
                RIGHT = 7,
                LEFT = 7,
                LOOK = 7,
                INVENTORY = 1,
                BROADCAST = 7,
                CONNECT_NBR = 0,
                FORK = 42,
                EJECT = 7,
                TAKE = 7,
                SET = 7,
                INCANTATION = 300
            };

            enum class SoundDirection : int {
                SAME_POSITION = 0,
                NORTH = 1,
                NORTHWEST = 2,
                WEST = 3,
                SOUTHWEST = 4,
                SOUTH = 5,
                SOUTHEAST = 6,
                EAST = 7,
                NORTHEAST = 8
            };

            CommandHandler(int &freq, int width, int height, int clientNb,
                zappy::game::MapServer &map, std::vector<std::shared_ptr<ITeams>> &teamList)
                : CommandHandlerGui(freq, width, height, clientNb, map, teamList) {};
            ~CommandHandler() = default;

            void processClientInput(
                std::string &input, zappy::game::ServerPlayer &player) override;

            void initCommandMap() override;

            int &getFreq() { return _freq; }

            void messageToGUI(const std::string &msg);


            void _executeCommand(zappy::game::ServerPlayer &player,
                std::function<void(ServerPlayer &, const std::string &)>
                    function,
                const std::string &args);

           private:
            void handleForward(zappy::game::ServerPlayer &player);
            void handleRight(zappy::game::ServerPlayer &player);
            void handleLeft(zappy::game::ServerPlayer &player);

            void handleLook(zappy::game::ServerPlayer &player);
            std::string _buildLookMessage(ServerPlayer &player);
            std::string _lookLine(ServerPlayer &player, size_t line);
            std::pair<int, int> _computeLookTarget(
                ServerPlayer &player, size_t line, int offset);
            std::string _getTileContent(size_t x, size_t y, bool isPlayerTile);
            bool _checkLastTileInLook(
                size_t playerLevel, size_t line, int offset);

            void handleInventory(zappy::game::ServerPlayer &player);

            void handleBroadcast(
                zappy::game::ServerPlayer &player, const std::string &arg);
            std::pair<int, int> _computeBroadcastDistance(
                int x1, int y1, int x2, int y2);
            int _computeSoundDirection(
                const ServerPlayer &player, const ServerPlayer &receiver);
            int _getSoundCardinalPoint(int relativeX, int relativeY);

            void handleConnectNbr(zappy::game::ServerPlayer &player);
            void handleFork(zappy::game::ServerPlayer &player);

            void handleEject(zappy::game::ServerPlayer &player)
            {
                (void)player;
            }

            void handleTake(
                zappy::game::ServerPlayer &player, const std::string &arg);
            void handleDrop(
                zappy::game::ServerPlayer &player, const std::string &arg);

            void handleIncantation(zappy::game::ServerPlayer &player);
            bool _checkIncantationConditions(const ServerPlayer &player);
            std::vector<std::weak_ptr<ServerPlayer>> _getPlayersOnTile(
                int x, int y, size_t level);
            bool _checkIncantationResources(size_t x, size_t y, size_t level);
            void _consumeElevationResources(size_t x, size_t y, size_t level);
            void _elevatePlayer(ServerPlayer &player);
            void _setPrayer(zappy::game::ServerPlayer &player);

            void _waitCommand(timeLimit limit);

            std::pair<size_t, size_t> _normalizeCoords(size_t x, size_t y);
            void _getDirectionVector(const Player &player, int &dx, int &dy);
            std::mutex _resourceMutex;
        };
    }  // namespace game

}  // namespace zappy
