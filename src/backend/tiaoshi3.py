import requests
import json

# 定义注册端点 URL
url = "http://localhost:5000/api/sign"

# 准备请求数据
data = {
    "username": "wenjie",
    "password": "123",
    "email": "testusera123@example.com"
}

# 设置请求头
headers = {
    "Content-Type": "application/json"
}

try:
    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 打印响应状态码和内容
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

    # 尝试解析 JSON 响应
    try:
        json_response = response.json()
        print("解析后的 JSON 响应:")
        print(json.dumps(json_response, indent=2, ensure_ascii=False))
    except ValueError:
        print("响应不是有效的 JSON 格式")

except requests.exceptions.RequestException as e:
    print(f"请求出错: {e}")

#
# import os
# import pandas as pd
#
#
#
# def get_sorted_jsons_with_index(folder_path, start_index=0):
#     """
#     获取目录下所有JSON文件的排序信息
#     :param folder_path: 目标目录路径
#     :param start_index: 起始索引（默认从0开始）
#     :return: 列表，每个元素为 (索引, 文件名, 文件路径)
#     """
#     json_extension = '.json'  # 只筛选JSON文件
#     json_files = []
#
#     # 遍历目录下的所有文件
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
#         # 筛选文件：必须是文件且以.json结尾（不区分大小写）
#         if os.path.isfile(file_path) and filename.lower().endswith(json_extension):
#             json_files.append((filename, file_path))  # 暂存 (文件名, 完整路径)
#
#     # 按文件名排序（与你处理图片的逻辑一致）
#     json_files_sorted = sorted(json_files, key=lambda x: x[0])
#
#     # 生成带索引的结果（索引从start_index开始）
#     return [(idx, filename, file_path) for idx, (filename, file_path) in
#             enumerate(json_files_sorted, start=start_index)]
#
#
#
# def get_sorted_images_with_index(folder_path, start_index=0):
#     image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif')
#     image_files = []
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
#         if os.path.isfile(file_path) and filename.lower().endswith(image_extensions):
#             image_files.append((filename, file_path))  # 暂存 (文件名, 完整路径)
#
#     image_files_sorted = sorted(image_files, key=lambda x: x[0])  # x[0] 指“文件名”
#
#     return [(idx, filename, file_path) for idx, (filename, file_path) in
#             enumerate(image_files_sorted, start=start_index)]
#
#
#
# if __name__ == "__main__":
#
#     target_folder = r"C:\Users\王彪\Desktop\flaskProject\绘图\test\TOC"
#     target_folder1 = r"C:\Users\王彪\Desktop\flaskProject\绘图\test\TOC\latex_per_equation"
#     df = pd.read_excel(r'C:\Users\王彪\Desktop\flaskProject\绘图\test\TOC\各级复杂度公式_每级最优_岩心TOC.xlsx')
#     df1 = pd.read_excel(r'C:\Users\王彪\Desktop\flaskProject\绘图\test\TOC\各级复杂度公式_逐式指标_岩心TOC.xlsx')
#     sorted_images = get_sorted_images_with_index(target_folder, start_index=0)
#     sorted_images1 = get_sorted_images_with_index(target_folder1, start_index=0)
#
#     print(sorted_images)
#     print(sorted_images1)
#
#
#     result = {}
#     result1 = {}
#     for idx in df['index']:
#         result[idx] = df[df['index'] == idx].drop(columns='index').to_dict(orient='records')[0]
#
#     for idx in df1['index']:
#         result1[idx] = df[df['index'] == idx].drop(columns='index').to_dict(orient='records')[0]
#
#     print(result)
#     print(result1)
#
#
#
#
#     json_folder = r"C:\Users\王彪\Desktop\flaskProject\绘图\test\TOC"
#
#     sorted_jsons = get_sorted_jsons_with_index(json_folder, start_index=0)
#
#     print(sorted_jsons)

# 遍历核心数据（以图像/公式/模型参数的索引为基准，取前3项可加[:3]）