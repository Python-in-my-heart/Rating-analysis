import pytest
import csv
import tempfile
import os
from main import (read_product_data, calculate_average_rating,
                  generate_average_rating_report)


def create_test_csv(content, suffix='.csv'):
    """Вспомогательная функция для создания
    временных CSV-файлов для тестирования."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False,
                                            suffix=suffix)
    writer = csv.writer(temp_file)
    writer.writerows(content)
    temp_file.close()
    return temp_file.name


class TestProductDataReading:
    """Тестирование чтения данных о продуктах из CSV-файлов."""

    def test_read_single_file(self):
        content = [
            ['name', 'brand', 'price', 'rating'],
            ['Product 1', 'Brand A', '100', '4.5'],
            ['Product 2', 'Brand B', '200', '3.5']
        ]
        file_path = create_test_csv(content)
        try:
            products = read_product_data([file_path])
            assert len(products) == 2
            assert products[0]['brand'] == 'Brand A'
            assert products[0]['rating'] == 4.5
            assert products[1]['brand'] == 'Brand B'
            assert products[1]['rating'] == 3.5
        finally:
            os.unlink(file_path)

    def test_read_multiple_files(self):
        content1 = [
            ['name', 'brand', 'price', 'rating'],
            ['Product 1', 'Brand A', '100', '4.5']
        ]
        content2 = [
            ['name', 'brand', 'price', 'rating'],
            ['Product 2', 'Brand B', '200', '3.5']
        ]
        file1 = create_test_csv(content1)
        file2 = create_test_csv(content2)
        try:
            products = read_product_data([file1, file2])
            assert len(products) == 2
            brands = {p['brand'] for p in products}
            assert brands == {'Brand A', 'Brand B'}
        finally:
            os.unlink(file1)
            os.unlink(file2)

    def test_rating_conversion(self):
        content = [
            ['name', 'brand', 'price', 'rating'],
            ['Product 1', 'Brand A', '100', '4.7']
        ]
        file_path = create_test_csv(content)
        try:
            products = read_product_data([file_path])
            assert isinstance(products[0]['rating'], float)
            assert products[0]['rating'] == 4.7
        finally:
            os.unlink(file_path)


class TestAverageRatingCalculation:
    """Тестирование вычисления средних рейтингов."""

    def test_single_brand_single_product(self):
        products = [
            {'brand': 'Brand A', 'rating': 4.5}
        ]
        averages = calculate_average_rating(products)
        assert averages == {'Brand A': 4.5}

    def test_single_brand_multiple_products(self):
        products = [
            {'brand': 'Brand A', 'rating': 4.0},
            {'brand': 'Brand A', 'rating': 5.0},
            {'brand': 'Brand A', 'rating': 3.0}
        ]
        averages = calculate_average_rating(products)
        assert averages == {'Brand A': 4.0}  # (4+5+3)/3

    def test_multiple_brands(self):
        products = [
            {'brand': 'Brand A', 'rating': 4.5},
            {'brand': 'Brand A', 'rating': 3.5},
            {'brand': 'Brand B', 'rating': 5.0},
            {'brand': 'Brand B', 'rating': 4.0}
        ]
        averages = calculate_average_rating(products)
        assert averages['Brand A'] == 4.0  # (4.5+3.5)/2
        assert averages['Brand B'] == 4.5  # (5.0+4.0)/2

    def test_empty_products(self):
        products = []
        averages = calculate_average_rating(products)
        assert averages == {}


class TestAverageRatingReport:
    """Тестирование генерации отчета о средних рейтингах."""

    def test_report_sorting(self):
        products = [
            {'brand': 'Brand C', 'rating': 3.0},
            {'brand': 'Brand A', 'rating': 5.0},
            {'brand': 'Brand B', 'rating': 4.0}
        ]
        report_data = generate_average_rating_report(products)
        # Должно быть отсортировано по рейтингу по убыванию
        assert report_data[0]['brand'] == 'Brand A'
        assert report_data[0]['rating'] == 5.0
        assert report_data[1]['brand'] == 'Brand B'
        assert report_data[1]['rating'] == 4.0
        assert report_data[2]['brand'] == 'Brand C'
        assert report_data[2]['rating'] == 3.0

    def test_report_indexing(self):
        products = [
            {'brand': 'Brand A', 'rating': 5.0},
            {'brand': 'Brand B', 'rating': 4.0}
        ]
        report_data = generate_average_rating_report(products)
        assert report_data[0][''] == 1
        assert report_data[1][''] == 2

    def test_rating_rounding(self):
        products = [
            {'brand': 'Brand A', 'rating': 4.567},
            {'brand': 'Brand B', 'rating': 3.333}
        ]
        report_data = generate_average_rating_report(products)
        assert report_data[0]['rating'] == 4.57
        assert report_data[1]['rating'] == 3.33

    def test_empty_report(self):
        products = []
        report_data = generate_average_rating_report(products)
        assert report_data == []


def test_integration_with_sample_data():
    """Интеграционный тест с примером данных из задачи."""
    # Создаем тестовые файлы, соответствующие примерам из задачи
    content1 = [
        ['name', 'brand', 'price', 'rating'],
        ['iphone 15 pro', 'apple', '999', '4.9'],
        ['galaxy s23 ultra', 'samsung', '1199', '4.8'],
        ['redmi note 12', 'xiaomi', '199', '4.6'],
        ['iphone 14', 'apple', '799', '4.7'],
        ['galaxy a54', 'samsung', '349', '4.2']
    ]
    content2 = [
        ['name', 'brand', 'price', 'rating'],
        ['poco x5 pro', 'xiaomi', '299', '4.4'],
        ['iphone se', 'apple', '429', '4.1'],
        ['galaxy z flip 5', 'samsung', '999', '4.6'],
        ['redmi 10c', 'xiaomi', '149', '4.1'],
        ['iphone 13 mini', 'apple', '599', '4.5']
    ]
    file1 = create_test_csv(content1)
    file2 = create_test_csv(content2)
    try:
        # Тестируем чтение данных
        products = read_product_data([file1, file2])
        assert len(products) == 10
        # Тестируем вычисление средних
        averages = calculate_average_rating(products)
        assert pytest.approx(averages['apple'], 0.01) == 4.55
        assert pytest.approx(averages['samsung'], 0.01) == 4.53
        assert pytest.approx(averages['xiaomi'], 0.01) == 4.37
        # Тестируем генерацию отчета
        report_data = generate_average_rating_report(products)
        assert report_data[0]['brand'] == 'apple'
        assert report_data[0]['rating'] == 4.55
        assert report_data[1]['brand'] == 'samsung'
        assert report_data[1]['rating'] == 4.53
        assert report_data[2]['brand'] == 'xiaomi'
        assert report_data[2]['rating'] == 4.37
    finally:
        os.unlink(file1)
        os.unlink(file2)
