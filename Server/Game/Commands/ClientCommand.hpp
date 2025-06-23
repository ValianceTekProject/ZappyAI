/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#pragma once

#include "ServerMap.hpp"
#include "ServerPlayer.hpp"
#include "Teams.hpp"
#include <functional>
#include <iostream>
#include <map>
#include <string>

namespace zappy {
    namespace game {

        class CommandHandler {
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

            CommandHandler(int freq, int width, int height, int clientNb,
                zappy::game::MapServer &map, std::vector<Team> &teamList)
                : _freq(freq), _widthMap(width), _heightMap(height),
                  _clientNb(clientNb), _map(map), _teamList(teamList) {};
            ~CommandHandler() = default;

            virtual void processClientInput(
                const std::string &input, zappy::game::ServerPlayer &player);

            virtual void initCommandMap();

           protected:
            int _freq;
            int _widthMap;
            int _heightMap;
            int _clientNb;
            MapServer &_map;
            std::unordered_map<std::string,
                std::function<void(ServerPlayer &, const std::string &)>>
                _commandMap;

            void _executeCommand(zappy::game::ServerPlayer &player,
                std::function<void(ServerPlayer &, const std::string &)>
                    function,
                const std::string &args);
            std::vector<Team> &_teamList;

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

            void handleIncantation(zappy::game::ServerPlayer &player)
            {
                (void)player;
            }

            void _waitCommand(timeLimit limit);

            std::pair<size_t, size_t> _normalizeCoords(size_t x, size_t y);
            void _getDirectionVector(const Player &player, int &dx, int &dy);
            std::mutex _resourceMutex;
        };
    }  // namespace game

}  // namespace zappy
