
import collections
import pandas as pd


def read_top_excel():
    data_top = collections.defaultdict(list)
    for sheet_name in pd.ExcelFile("头部博主统计.xlsx").sheet_names:
        if sheet_name == "开源中国（郝祺）":
            d = pd.read_excel("头部博主统计.xlsx", sheet_name=sheet_name, usecols=[0], names=None)
            df_li = d.values.tolist()
            for data in df_li:
                data_top.setdefault("oschina", []).append(data[0])
        elif sheet_name == "oppo 社区（贾双月）":
            d = pd.read_excel("头部博主统计.xlsx", sheet_name=sheet_name, usecols=[0], names=None)
            df_li = d.values.tolist()
            for data in df_li:
                data_top.setdefault("oppo", []).append(data[0])
        elif sheet_name == "数字尾巴（侯睿）":
            d = pd.read_excel("头部博主统计.xlsx", sheet_name=sheet_name, usecols=[0], names=None)
            df_li = d.values.tolist()
            for data in df_li:
                data_top.setdefault("dgtle", []).append(data[0])
    return data_top
