/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AssetPaths.hpp
*/

#pragma once

#include <string>

namespace zappy {
    namespace gui {
        namespace raylib {
            namespace assets {
                constexpr const char *ASSETS_PATH = "src/Renderer/Raylib/Assets/";

                // Floor assets
                inline std::string FLOOR_PATH = std::string(ASSETS_PATH) + "grass.jpg";

                // Basic Scene assets
                inline std::string BASIC_SCENE_PATH = std::string(ASSETS_PATH) + "Basic/";

                inline std::string BASIC_PLAYER_PATH = std::string(BASIC_SCENE_PATH) + "player.glb";

                // Pokemon Scene assets
            }
        }
    }
}
