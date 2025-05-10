import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rc('font', family='Microsoft JhengHei')  # 設定中文字型
plt.rcParams['axes.unicode_minus'] = False  # 正常顯示負號

# 讓使用者輸入檔案名稱
file_name = input('請輸入要分析的 CSV 檔案名稱（例如 202505_交易.csv）：')
file_path = os.path.join('data', file_name)

# 讀取 CSV，跳過第一列標題
raw_df = pd.read_csv(file_path, header=1)

# 定義三組資料的欄位
groups = [
    {'name': '國泰', 'cols': ['日期', '項目', '金額', '類別']},
    {'name': '永豐', 'cols': ['日期', '項目', '金額', '類別']},
    {'name': '現金', 'cols': ['日期', '項目', '金額', '類別']},
]

# 對應到 csv 欄位
col_indices = [0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13]

# 萃取三組資料
all_data = []
for i, group in enumerate(groups):
    start = i * 4 + i  # 每組之間有一個空欄
    cols = raw_df.columns[start:start+4]
    df = raw_df[list(cols)].copy()
    df.columns = group['cols']
    df['來源'] = group['name']
    all_data.append(df)

# 合併三組資料
merged_df = pd.concat(all_data, ignore_index=True)

# 移除全空白列與項目為「總計」的資料列（含前後空白）
merged_df = merged_df.dropna(how='all')
merged_df = merged_df[~(merged_df['項目'].astype(str).str.strip() == '總計')]

# 將金額轉為數值，移除無效資料（NaN 或 0）
merged_df['金額'] = pd.to_numeric(merged_df['金額'], errors='coerce')
merged_df = merged_df.dropna(subset=['金額'])
merged_df = merged_df[merged_df['金額'] != 0]

# 對現金組，若金額有值但類別為空，強制標註為「現金」
merged_df.loc[(merged_df['來源'] == '現金') & (merged_df['金額'].notna()) & ((merged_df['類別'].isna()) | (merged_df['類別'].astype(str).str.strip() == '')), '類別'] = '現金'

# 除錯：印出即將被標註為「其他」的資料
print('--- 以下資料將被歸類為「其他」 ---')
print(merged_df[(merged_df['類別'].isna()) | (merged_df['類別'].astype(str).str.strip() == '')])

# 將空白或 NaN 的類別標示為「其他」
merged_df['類別'] = merged_df['類別'].fillna('其他')
merged_df.loc[merged_df['類別'].astype(str).str.strip() == '', '類別'] = '其他'

# 依據類別加總金額
category_sum = merged_df.groupby('類別')['金額'].sum()

# 顯示總金額
sum_amount = merged_df["金額"].sum()
print(f'總金額：{sum_amount:,.2f}')

# 準備標籤：類別+金額
labels = [f'{cat} {amt:,.0f}元' for cat, amt in category_sum.items()]

# 畫圓餅圖
plt.figure(figsize=(8, 8))
plt.pie(category_sum, labels=labels, autopct='%1.1f%%', startangle=140, labeldistance=1.1)
plt.title('消費類別占比分析', pad=40)
plt.suptitle(f'總金額：{sum_amount:,.0f}元', y=0.92, fontsize=14, color='gray')
plt.axis('equal')

# 儲存圖片
img_dir = 'img'
os.makedirs(img_dir, exist_ok=True)
img_name = os.path.splitext(os.path.basename(file_name))[0] + '.png'
img_path = os.path.join(img_dir, img_name)
plt.savefig(img_path, bbox_inches='tight', dpi=150)
print(f'圓餅圖已儲存至: {img_path}')

plt.show()
