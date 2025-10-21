import argparse
import csv
from collections import defaultdict
import sys
from tabulate import tabulate


def read_product_data(file_paths):
    """Читает данные о продуктах из нескольких CSV-файлов."""
    products = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['rating'] = float(row['rating'])
                products.append(row)
    return products


def calculate_average_rating(products):
    """Вычисляет средний рейтинг для каждого бренда."""
    brand_ratings = defaultdict(list)
    for product in products:
        brand_ratings[product['brand']].append(product['rating'])
    averages = {}
    for brand, ratings in brand_ratings.items():
        averages[brand] = sum(ratings) / len(ratings)
    return averages


def generate_average_rating_report(products):
    """Генерирует отчет о среднем рейтинге,
    отсортированный по убыванию рейтинга."""
    averages = calculate_average_rating(products)

    # Сортируем бренды по среднему рейтингу (по убыванию)
    sorted_brands = sorted(averages.items(),
                           key=lambda x: x[1],
                           reverse=True)

    # Форматируем результаты с индексом
    report_data = []
    for i, (brand, avg_rating) in enumerate(sorted_brands, 1):
        report_data.append({
            '': i,
            'brand': brand,
            'rating': round(avg_rating, 2)
        })
    return report_data


# Реестр генераторов отчетов для легкого добавления новых отчетов
REPORT_GENERATORS = {
    'average-rating': generate_average_rating_report,
}


def main():
    parser = argparse.ArgumentParser(description='Генератор'
                                     'отчетов о продуктах')
    parser.add_argument('--files', nargs='+', required=True,
                        help='CSV-файлы с продуктами для обработки')
    parser.add_argument('--report', required=True,
                        choices=REPORT_GENERATORS.keys(),
                        help='Тип отчета для генерации')
    args = parser.parse_args()

    try:
        # Читаем и обрабатываем данные
        products = read_product_data(args.files)

        # Генерируем запрошенный отчет
        report_generator = REPORT_GENERATORS[args.report]
        report_data = report_generator(products)

        # Выводим отчет
        if report_data:
            print(tabulate(report_data, headers='keys', tablefmt='grid'))
        else:
            print("Нет данных для отчета")

    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
