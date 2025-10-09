import csv
import random
import statistics
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

def generate_csv_file(filename, num_rows=100):
    categories = ['A', 'B', 'C', 'D']
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Категория', 'Значение'])
        
        for i in range(num_rows):
            category = random.choice(categories)
            value = round(random.uniform(1.0, 100.0), 2)
            writer.writerow([category, value])
    
    print(f"Сгенерирован файл: {filename}")

def process_single_file(filename):
    category_data = {}

    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row['Категория']
            value = float(row['Значение'])
        
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(value)
    
    results = {}
    for category, values in category_data.items():
        if len(values) > 1:
            median = statistics.median(values)
            stdev = statistics.stdev(values)
            results[category] = (median, stdev)
        elif len(values) == 1:
            results[category] = (values[0], 0.0)
    
    return results


def process_all_files_parallel(file_list):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_single_file, file_list))
    
    return results

def combine_results(all_results):
    category_medians = {} 
    
    for file_result in all_results:
        for category, (median, stdev) in file_result.items():
            if category not in category_medians:
                category_medians[category] = []
            category_medians[category].append(median)
    
    final_results = {}
    for category, medians in category_medians.items():
        if len(medians) > 1:
            median_of_medians = statistics.median(medians)
            stdev_of_medians = statistics.stdev(medians)
        elif len(medians) == 1:
            median_of_medians = medians[0]
            stdev_of_medians = 0.0
        else:
            continue
        
        final_results[category] = (median_of_medians, stdev_of_medians)
    
    return final_results

def save_results_to_csv(results, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Категория', 'Медиана_медиан', 'Стандартное_отклонение_медиан'])
        
        for category in sorted(results.keys()):
            median, stdev = results[category]
            writer.writerow([category, round(median, 2), round(stdev, 2)])

def main():
    csv_files = []
    for i in range(1, 6):
        filename = f"data_{i}.csv"
        generate_csv_file(filename, num_rows=50)
        csv_files.append(filename)
    
    print("\n" + "="*50)
    print("Начинаем параллельную обработку файлов...")
    
    all_results = process_all_files_parallel(csv_files)
    
    print("\nПромежуточные результаты по файлам:")
    for i, result in enumerate(all_results, 1):
        print(f"\nФайл data_{i}.csv:")
        for category in sorted(result.keys()):
            median, stdev = result[category]
            print(f"  {category}: медиана = {median:.2f}, отклонение = {stdev:.2f}")
    
    final_results = combine_results(all_results)
    
    print("\n" + "="*50)
    print("Финальные результаты (медиана медиан и стандартное отклонение медиан):")
    
    for category in sorted(final_results.keys()):
        median, stdev = final_results[category]
        print(f"{category}: медиана медиан = {median:.2f}, стандартное отклонение медиан = {stdev:.2f}")
    
    save_results_to_csv(final_results, "final_results.csv")
    print(f"\nРезультаты сохранены в файл: final_results.csv")
    
if __name__ == "__main__":
    main()