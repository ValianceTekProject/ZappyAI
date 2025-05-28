/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GUI.hpp
*/

#pragma once

#include "GUIError.hpp"
#include "ParsingError.hpp"
#include "IRenderer.hpp"
#include "GameState.hpp"

#include <string>
#include <memory>

namespace gui
{
    class ZappyGui
    {
        public:
            ZappyGui();
            ~ZappyGui() = default;

            void parseArgs(int argc, char const *argv[]);

            void run();

        private:
            std::string _ip;
            int _port;

            int _frequency;

            std::unique_ptr<IRenderer> _renderer;

            GameState _gameState;
    };
} // namespace gui

