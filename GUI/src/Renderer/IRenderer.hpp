/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IRenderer.hpp
*/

namespace zappy {
    namespace gui {
        class IRenderer
        {
            public:
                virtual ~IRenderer() = default;

                virtual void init() = 0;

                virtual void handleInput() = 0;
                virtual void update() = 0;

                virtual void render() = 0;

                virtual void close() = 0;
        };
    }
}
