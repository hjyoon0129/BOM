import pandas as pd

# 주어진 데이터
data = {
    "FREQ": [
        19.95, 20.24, 20.54, 20.83, 21.13, 21.44, 21.75, 22.07, 22.39, 22.71,
        # 나머지 데이터는 생략
    ],
    "O": [
        55.41, 56.01, 58.45, 58.69, 57.72, 57.32, 57.46, 57.56, 58.02, 58.34,
        # 나머지 데이터는 생략
    ],
}

# 데이터프레임 생성
df = pd.DataFrame(data)

# 스무딩을 위한 함수 정의
def octave_smoothing(data_series, octave):
    smoothed_values = []
    for i in range(len(data_series)):
        start_index = max(0, i - octave // 2)
        end_index = min(len(data_series), i + octave // 2 + 1)
        window_data = data_series[start_index:end_index]
        smoothed_value = sum(window_data) / len(window_data)
        smoothed_values.append(smoothed_value)
    return smoothed_values

# 옥타브 스무딩 적용
octave = 3  # 이 옥타브 크기를 조정하여 스무딩 수준을 조절할 수 있습니다.
smoothed_o = octave_smoothing(df['O'], octave)
smoothed_x = octave_smoothing(df['X'], octave)

# 데이터프레임에 추가
df['O_smoothed'] = smoothed_o
df['X_smoothed'] = smoothed_x

# 결과 출력
print(df)

# 데이터프레임을 엑셀 파일로 저장
df.to_excel('smoothed_data.xlsx', index=False)