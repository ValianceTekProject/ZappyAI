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


namespace zappy {
    namespace game {

        class CommandHandler {
           public:
            CommandHandler();
            ~CommandHandler() = default;

            void processClientInput(const std::string &input);
           private:
            std::map<std::string, std::function<void()>> _commandMap;

            std::string _getFirstWord(const std::string &input) const;
        
            void handleForward() { std::cout << "Forward\n"; }
            void handleRight() { std::cout << "Right\n"; }
            void handleLeft() { std::cout << "Left\n"; }
            void handleLook() { std::cout << "Look\n"; }
            void handleInventory() { std::cout << "Inventory\n"; }
            void handleBroadcast() { std::cout << "Broadcast\n"; }
            void handleConnectNbr() { std::cout << "Connect_nbr\n"; }
            void handleFork() { std::cout << "Fork\n"; }
            void handleEject() { std::cout << "Eject\n"; }
            void handleTake() { std::cout << "Take object\n"; }
            void handleDrop() { std::cout << "Set object (drop)\n"; }
            void handleIncantation() { std::cout << "Incantation\n"; }
        };

    }  // namespace server

}  // namespace zappy
