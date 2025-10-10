import random
import statistics
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

def generate_csv_file(filename, num_rows=100):
    categories = ['A', 'B', 'C', 'D']
    
    data = {
        'Категория': [random.choice(categories) for _ in range(num_rows)],
        'Значение': [round(random.uniform(1.0, 100.0), 2) for _ in range(num_rows)]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Сгенерирован файл: {filename}")

def process_single_file(filename):
    df = pd.read_csv(filename, encoding='utf-8')
    results = {}
    for category in df['Категория'].unique():
        values = df[df['Категория'] == category]['Значение'].values
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
    all_data = []
    for i, file_result in enumerate(all_results):
        for category, (median, stdev) in file_result.items():
            all_data.append({
                'Файл': f'data_{i+1}.csv',
                'Категория': category,
                'Медиана': median,
                'Отклонение': stdev
            })
    df = pd.DataFrame(all_data)

    final_results = {}
    for category in df['Категория'].unique():
        category_medians = df[df['Категория'] == category]['Медиана'].values
        if len(category_medians) > 1:
            median_of_medians = statistics.median(category_medians)
            stdev_of_medians = statistics.stdev(category_medians)
        elif len(category_medians) == 1:
            median_of_medians = category_medians[0]
            stdev_of_medians = 0.0
        else:
            continue
        final_results[category] = (median_of_medians, stdev_of_medians)
    
    return final_results, df  # Возвращаем также DataFrame для анализа

def save_results_to_csv(results, filename):
    data = []
    for category in sorted(results.keys()):
        median, stdev = results[category]
        data.append({
            'Категория': category,
            'Медиана_медиан': round(median, 2),
            'Стандартное_отклонение_медиан': round(stdev, 2)
        })
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')

def main():
    csv_files = []
    for i in range(1, 6): #генерация 5 файлов
        filename = f"data_{i}.csv"
        generate_csv_file(filename, num_rows=50)
        csv_files.append(filename)
    print("\n" + "="*50)
    print("Начинаем параллельную обработку файлов...")
    
    all_results = process_all_files_parallel(csv_files)
    
    print("\nПРОМЕЖУТОЧНЫЕ РЕЗУЛЬТАТЫ ПО ФАЙЛАМ:")
    for i, result in enumerate(all_results, 1):
        print(f"\nФайл data_{i}.csv:")
        for category in sorted(result.keys()):
            median, stdev = result[category]
            print(f"  {category}: медиана = {median:.2f}, отклонение = {stdev:.2f}")

    final_results, all_results_df = combine_results(all_results)
    
    print("\n" + "="*50)
    print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    print("(медиана медиан и стандартное отклонение медиан)")
    print("="*50)
    
    for category in sorted(final_results.keys()):
        median, stdev = final_results[category]
        print(f"{category}: медиана медиан = {median:.2f}, стандартное отклонение медиан = {stdev:.2f}")
    
    save_results_to_csv(final_results, "final_results.csv")
    print(f"\nРезультаты сохранены в файл: final_results.csv")
    
if __name__ == "__main__":
    main()
