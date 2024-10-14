from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Данные о рецептах
DATA = {
    'omlet': {
        'яйца, шт': 2,
        'молоко, л': 0.1,
        'соль, ч.л.': 0.5,
    },
    'pasta': {
        'макароны, г': 0.3,
        'сыр, г': 0.05,
    },
    'buter': {
        'хлеб, ломтик': 1,
        'колбаса, ломтик': 1,
        'сыр, ломтик': 1,
        'помидор, долька': 1,
    }
}

class RecipeRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Парсим путь и параметры запроса
        url_components = urlparse(self.path)
        dish = url_components.path.strip('/')  # Получаем название блюда
        query_params = parse_qs(url_components.query)

        # Проверяем, есть ли такой рецепт
        recipe = DATA.get(dish)
        if not recipe:
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')  # Указываем кодировку
            self.end_headers()
            self.wfile.write(f"Рецепт для {dish} не найден.".encode('utf-8'))
            return

        # Обрабатываем параметр servings
        servings = query_params.get('servings', [1])[0]
        try:
            servings = int(servings)
            if servings <= 0:
                raise ValueError
        except ValueError:
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')  # Указываем кодировку
            self.end_headers()
            self.wfile.write("Параметр servings должен быть положительным целым числом.".encode('utf-8'))
            return

        # Масштабируем ингредиенты
        scaled_recipe = {ingredient: amount * servings for ingredient, amount in recipe.items()}

        # Отправляем успешный ответ
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')  # Указываем кодировку
        self.end_headers()

        # Формируем ответ
        response = "\n".join([f"{ingredient}: {amount}" for ingredient, amount in scaled_recipe.items()])
        self.wfile.write(response.encode('utf-8'))

# Запуск сервера
def run(server_class=HTTPServer, handler_class=RecipeRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущен на порту {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
