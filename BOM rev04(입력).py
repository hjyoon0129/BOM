import pandas as pd
import sqlite3



# 엑셀 파일을 읽어와 SQLite에 저장하는 함수
def load_excel_to_sqlite(file_path, table_name):
    # 엑셀 파일 읽기
    df_list = []
    for filename in csv_filenames:
        # 1~4번째 라인을 스킵하고 5번째 라인부터 데이터를 읽어들임
        df = pd.read_csv(filename, encoding='latin-1', skiprows=4, header=0)
        # 각 csv파일중 원하는 행 추출
        df = df.iloc[:, [0, 1, 2]]
        # 파일 이름을 가져와서 열 이름 변경
        spl0_col_name = os.path.basename(filename) + "_SPL0"
        imp_col_name = os.path.basename(filename) + "_Imp"
        df.columns = ["Frequency", spl0_col_name, imp_col_name]
        df_list.append(df)

    # 모든 데이터프레임을 병합하여 하나의 데이터프레임으로 만듦
    df = pd.concat(df_list, axis=1)
    df = df.loc[:, ~df.T.duplicated()]  # 동일한 X축 하나로 병합

    # 결과를 엑셀 파일로 저장
    output_filename = "merged.xlsx"
    df.to_excel(output_filename, index=False, header=True)

    # SQLite 데이터베이스 연결
    connection = sqlite3.connect('data.db')

    # 데이터프레임을 SQLite 테이블로 저장
    df.to_sql(table_name, connection, if_exists='replace', index=False)

    # 연결 종료
    connection.close()


# 엑셀 파일 경로와 테이블 이름 설정
file_path = 'your_excel_file.xlsx'  # 엑셀 파일 경로를 지정해주세요
table_name = 'excel_data'  # SQLite 테이블 이름을 지정해주세요

# SQLite에 데이터 저장
load_excel_to_sqlite(file_path, table_name)