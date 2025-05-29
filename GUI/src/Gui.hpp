/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Gui.hpp
*/

#pragma once

#include "GuiError.hpp"
#include "ParsingError.hpp"
#include "IRenderer.hpp"
#include "GameState.hpp"

#include <string>
#include <sstream>
#include <memory>

namespace zappy {
    namespace gui {
        class Gui
        {
            public:
                Gui();
                ~Gui() = default;

                void parseArgs(int argc, char const *argv[]);
                void init();

                void run();

            private:
                std::string _ip;
                size_t _port;

                size_t _frequency;

                std::unique_ptr<IRenderer> _renderer;

                game::GameState _gameState;
        };
    }
}

