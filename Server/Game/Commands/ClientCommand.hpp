/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#pragma once

#include "ServerMap.hpp"
#include "ServerPlayer.hpp"
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

            CommandHandler(int freq, int width, int height, int clientNb,
                zappy::game::MapServer &map)
                : _freq(freq), _widthMap(width), _heightMap(height),
                  _clientNb(clientNb), _map(map) {};
            ~CommandHandler() = default;

            virtual void processClientInput(const std::string &input, zappy::game::ServerPlayer &player);

            virtual void initCommandMap();

           protected:
            int _freq;
            int _widthMap;
            int _heightMap;
            int _clientNb;
            zappy::game::MapServer &_map;
            std::unordered_map<std::string,
                std::function<void(ServerPlayer &, const std::string &)>>
                _commandMap;

            void _executeCommand(zappy::game::ServerPlayer &player,
                std::function<void(ServerPlayer &, const std::string &)>
                    function,
                const std::string &args);
           private:
            // TODO dont forget: adding check of chrono start in non complete command function
            void handleForward(zappy::game::ServerPlayer &player);
            void handleRight(zappy::game::ServerPlayer &player);
            void handleLeft(zappy::game::ServerPlayer &player);

            void handleLook(zappy::game::ServerPlayer &player)
            {
                (void)player;
            }

            void handleInventory(zappy::game::ServerPlayer &player);
            void handleBroadcast(
                zappy::game::ServerPlayer &player, const std::string &arg);
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

            std::mutex _resourceMutex;
        };
    }  // namespace game

}  // namespace zappy
