/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientCommand
*/

#pragma once

#include <functional>
#include <iostream>
#include <map>
#include <string>
#include "ServerPlayer.hpp"


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

            CommandHandler(int freq, int width, int height, int clientNb) : _freq(freq), _widthMap(width), _heightMap(height), _clientNb(clientNb) {};
            ~CommandHandler() = default;

            void processClientInput(const std::string &input, zappy::game::ServerPlayer &player);

            void initCommandMap(zappy::game::ServerPlayer &player);

           private:
            int _freq;
            int _widthMap;
            int _heightMap;
            int _clientNb;
            std::map<std::string, std::function<void()>> _commandMap;

            std::string _getFirstWord(const std::string &input) const;
        

            // TODO dont forget: adding check of chrono start in non complete command function
            void handleForward(zappy::game::ServerPlayer &player);
            void handleRight(zappy::game::ServerPlayer &player);
            void handleLeft(zappy::game::ServerPlayer &player);
            void handleLook(zappy::game::ServerPlayer &player) { (void)player; }
            void handleInventory(zappy::game::ServerPlayer &player);
            void handleBroadcast(zappy::game::ServerPlayer &player);
            void handleConnectNbr(zappy::game::ServerPlayer &player);
            void handleFork(zappy::game::ServerPlayer &player);
            void handleEject(zappy::game::ServerPlayer &player) { (void)player; }
            void handleTake(zappy::game::ServerPlayer &player) { (void)player; }
            void handleDrop(zappy::game::ServerPlayer &player) { (void)player; }
            void handleIncantation(zappy::game::ServerPlayer &player) { (void)player; }
        };

    }  // namespace server

}  // namespace zappy
